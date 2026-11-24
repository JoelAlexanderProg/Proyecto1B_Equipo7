"""Pruebas de sistema del recorrido del cliente (PN-01) a través de HTTP."""

import re

from tests.sistema.conftest import DATOS_ANA, DATOS_LUIS, pedir, registrar

BOLON, EMPANADA, HUMITA, CAFE = "ALI-001", "ALI-002", "ALI-004", "BEB-001"
PATRON_CODIGO = re.compile(r"/pedidos/([A-Z2-9]{3}-[A-Z2-9]{3})$")


def test_menu_publico_muestra_precios_y_disponibilidad(navegador):
    pagina = navegador.get("/")
    assert pagina.status_code == 200
    assert "Bolón de verde con queso" in pagina.text
    assert "$1,75" in pagina.text
    assert "No disponible" in pagina.text
    assert 'name="cant-' not in pagina.text


def test_registro_inicia_sesion_y_muestra_codigo_de_cliente(navegador):
    pagina = registrar(navegador)
    assert pagina.status_code == 200
    assert "CLI-0001" in pagina.text
    assert f'name="cant-{BOLON}"' in pagina.text
    assert f'name="cant-{HUMITA}"' not in pagina.text


def test_registro_con_cedula_invalida_muestra_el_motivo(navegador):
    pagina = registrar(navegador, {**DATOS_ANA, "cedula": "1712345678"})
    assert pagina.status_code == 422
    assert "La cédula no es válida" in pagina.text


def test_revisar_sin_sesion_redirige_al_ingreso(navegador):
    pagina = navegador.post("/pedido/revisar", data={f"cant-{BOLON}": "1"})
    assert pagina.url.path == "/ingresar"


def test_revisar_sin_productos_no_continua(navegador):
    registrar(navegador)
    pagina = navegador.post("/pedido/revisar", data={f"cant-{BOLON}": "0"})
    assert pagina.status_code == 422
    assert "al menos un producto" in pagina.text


def test_revisar_rechaza_cantidades_no_validas(navegador):
    registrar(navegador)
    assert navegador.post("/pedido/revisar", data={f"cant-{BOLON}": "21"}).status_code == 422
    assert navegador.post("/pedido/revisar", data={f"cant-{BOLON}": "-1"}).status_code == 422
    pagina = navegador.post("/pedido/revisar", data={f"cant-{BOLON}": "dos"})
    assert pagina.status_code == 422
    assert "números enteros" in pagina.text


def test_revisar_rechaza_producto_no_disponible(navegador):
    registrar(navegador)
    pagina = navegador.post("/pedido/revisar", data={f"cant-{HUMITA}": "1"})
    assert pagina.status_code == 422
    assert "Humita ya no está disponible" in pagina.text


def test_recorrido_completo_hasta_el_codigo_de_retiro(navegador):
    registrar(navegador)
    revision = navegador.post(
        "/pedido/revisar", data={f"cant-{BOLON}": "1", f"cant-{EMPANADA}": "2"}
    )
    assert "$3,35" in revision.text
    assert "$0,80 c/u" in revision.text
    confirmacion = pedir(navegador, {BOLON: 1, EMPANADA: 2})
    codigo = PATRON_CODIGO.search(confirmacion.url.path).group(1)
    assert codigo in confirmacion.text
    assert "Pendiente" in confirmacion.text
    assert codigo in navegador.get("/mis-pedidos").text


def test_cambio_de_precio_antes_de_confirmar_muestra_el_nuevo_total(navegador, servicios):
    registrar(navegador)
    revision = navegador.post("/pedido/revisar", data={f"cant-{CAFE}": "2"})
    total = revision.text.split('name="total_revisado" value="')[1].split('"')[0]
    servicios.menu.actualizar(
        CAFE, nombre="Café pasado", categoria="BEBIDA", precio="0.90", disponible=True
    )
    pagina = navegador.post("/pedido/confirmar", data={"total_revisado": total})
    assert "Un precio cambió" in pagina.text
    assert "$1,80" in pagina.text
    assert servicios.pedidos.pedidos_de_cliente(1) == []


def test_producto_agotado_antes_de_confirmar_no_se_confirma(navegador, servicios):
    registrar(navegador)
    revision = navegador.post("/pedido/revisar", data={f"cant-{CAFE}": "1"})
    total = revision.text.split('name="total_revisado" value="')[1].split('"')[0]
    servicios.menu.cambiar_disponibilidad(CAFE, False)
    pagina = navegador.post("/pedido/confirmar", data={"total_revisado": total})
    assert pagina.status_code == 422
    assert "Café pasado ya no está disponible" in pagina.text


def test_un_cliente_no_ve_el_pedido_de_otro(navegador, otro_navegador):
    registrar(navegador)
    ruta = pedir(navegador, {CAFE: 1}).url.path
    registrar(otro_navegador, DATOS_LUIS)
    assert otro_navegador.get(ruta).status_code == 404


def test_ingreso_con_correo_y_cedula(navegador, otro_navegador):
    registrar(navegador)
    fallido = otro_navegador.post(
        "/ingresar", data={"correo": DATOS_ANA["correo"], "cedula": "0102030400"}
    )
    assert fallido.status_code == 422
    correcto = otro_navegador.post(
        "/ingresar", data={"correo": DATOS_ANA["correo"], "cedula": DATOS_ANA["cedula"]}
    )
    assert f'name="cant-{BOLON}"' in correcto.text


def test_salir_cierra_la_sesion(navegador):
    registrar(navegador)
    navegador.post("/salir")
    assert navegador.get("/mis-pedidos").url.path == "/ingresar"


def test_api_de_productos_y_healthcheck(navegador):
    assert navegador.get("/health").json() == {"estado": "ok", "version": "1.0.0"}
    productos = navegador.get("/api/v1/productos", params={"disponibles": "true"}).json()
    assert "Humita" not in [p["nombre"] for p in productos]
    assert productos[0] == {
        "codigo": "ALI-005",
        "nombre": "Almuerzo del día",
        "categoria": "ALIMENTO",
        "precio": "3.00",
        "disponible": True,
    }


def test_fuentes_se_sirven_con_su_tipo(navegador):
    respuesta = navegador.get("/static/fonts/inter.woff2")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "font/woff2"


def test_pagina_inexistente_muestra_error_amigable(navegador):
    pagina = navegador.get("/no-existe")
    assert pagina.status_code == 404
    assert "No encontramos esa página" in pagina.text


def test_rutas_del_cliente_exigen_sesion(navegador):
    assert navegador.post("/pedido/confirmar", data={"total_revisado": "1"}).url.path == "/ingresar"
    assert navegador.get("/pedidos/AAA-AAA").url.path == "/ingresar"


def test_pedido_inexistente_responde_404(navegador):
    registrar(navegador)
    assert navegador.get("/pedidos/AAA-AAA").status_code == 404


def test_total_revisado_alterado_no_confirma(navegador, servicios):
    registrar(navegador)
    navegador.post("/pedido/revisar", data={f"cant-{CAFE}": "1", "otro-campo": "x"})
    pagina = navegador.post("/pedido/confirmar", data={"total_revisado": "no-es-un-monto"})
    assert "Un precio cambió" in pagina.text
    assert servicios.pedidos.pedidos_de_cliente(1) == []


def test_registro_duplicado_muestra_el_motivo(navegador, otro_navegador):
    registrar(navegador)
    pagina = registrar(otro_navegador)
    assert pagina.status_code == 422
    assert "Ya existe un cliente con esa cédula" in pagina.text


def test_api_inexistente_responde_json(navegador):
    respuesta = navegador.get("/api/v1/no-existe")
    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Not Found"}
