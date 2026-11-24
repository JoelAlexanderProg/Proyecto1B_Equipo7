"""Pruebas de sistema del personal: preparación y entrega (PN-02) y mantenimiento del menú."""

from decimal import Decimal

import pytest

from cafeteria.dominio.modelos import EstadoPedido
from tests.sistema.conftest import CLAVE_PERSONAL, pedir, registrar

CAFE, CAPUCHINO, HUMITA = "BEB-001", "BEB-002", "ALI-004"


@pytest.fixture
def personal(otro_navegador):
    otro_navegador.post("/personal/ingresar", data={"usuario": "personal", "clave": CLAVE_PERSONAL})
    return otro_navegador


@pytest.fixture
def pedido(navegador, servicios):
    """Pedido confirmado por un cliente desde su propio navegador."""
    registrar(navegador)
    respuesta = pedir(navegador, {CAFE: 2})
    return servicios.pedidos.obtener_por_codigo(respuesta.url.path.rsplit("/", 1)[1])


def test_tablero_exige_ingreso_del_personal(navegador):
    assert navegador.get("/personal").url.path == "/personal/ingresar"
    registrar(navegador)
    assert navegador.get("/personal/menu").url.path == "/personal/ingresar"


def test_ingreso_con_clave_incorrecta(otro_navegador):
    pagina = otro_navegador.post("/personal/ingresar", data={"usuario": "personal", "clave": "x"})
    assert pagina.status_code == 422
    assert "Usuario o clave incorrectos" in pagina.text


def test_flujo_de_preparacion_y_entrega(pedido, personal, navegador, servicios):
    tablero = personal.get("/personal")
    assert pedido.codigo_retiro in tablero.text
    assert "Iniciar preparación" in tablero.text

    pagina = personal.post(f"/personal/pedidos/{pedido.id}/avanzar")
    assert "En preparación." in pagina.text
    pagina = personal.post(f"/personal/pedidos/{pedido.id}/avanzar")
    assert "Listo para retirar." in pagina.text
    assert "Código que presenta el cliente" in pagina.text

    pagina = personal.post(f"/personal/pedidos/{pedido.id}/entregar", data={"codigo": "ZZZ-ZZZ"})
    assert f"Pedido {pedido.codigo_retiro}: no se registró la entrega" in pagina.text
    assert servicios.pedidos.obtener(pedido.id).estado is EstadoPedido.LISTO_PARA_RETIRAR

    escrito = pedido.codigo_retiro.replace("-", "").lower()
    pagina = personal.post(f"/personal/pedidos/{pedido.id}/entregar", data={"codigo": escrito})
    assert f"Pedido {pedido.codigo_retiro} entregado." in pagina.text
    assert "1 entregado hoy" in pagina.text
    assert "Entregado" in navegador.get(f"/pedidos/{pedido.codigo_retiro}").text


def test_listo_no_avanza_sin_codigo(pedido, personal, servicios):
    servicios.pedidos.avanzar(pedido.id)
    servicios.pedidos.avanzar(pedido.id)
    pagina = personal.post(f"/personal/pedidos/{pedido.id}/avanzar")
    assert "se debe verificar el código de retiro" in pagina.text
    assert servicios.pedidos.obtener(pedido.id).estado is EstadoPedido.LISTO_PARA_RETIRAR


def test_pendiente_no_se_puede_entregar(pedido, personal, servicios):
    pagina = personal.post(
        f"/personal/pedidos/{pedido.id}/entregar", data={"codigo": pedido.codigo_retiro}
    )
    assert "solo se entrega cuando está Listo para retirar" in pagina.text
    assert servicios.pedidos.obtener(pedido.id).estado is EstadoPedido.PENDIENTE


def test_tablero_ordena_del_mas_antiguo_al_mas_reciente(navegador, personal):
    registrar(navegador)
    primero = pedir(navegador, {CAFE: 1}).url.path.rsplit("/", 1)[1]
    segundo = pedir(navegador, {CAPUCHINO: 1}).url.path.rsplit("/", 1)[1]
    texto = personal.get("/personal").text
    assert texto.index(primero) < texto.index(segundo)


def test_agregar_producto_valida_y_asigna_codigo(personal):
    invalido = personal.post(
        "/personal/menu",
        data={"nombre": "Tigrillo", "categoria": "ALIMENTO", "precio": "-1", "disponible": "1"},
    )
    assert invalido.status_code == 422
    assert "mayor que cero" in invalido.text
    valido = personal.post(
        "/personal/menu",
        data={"nombre": "Tigrillo", "categoria": "ALIMENTO", "precio": "2,50", "disponible": "1"},
    )
    assert "Tigrillo se agregó al menú con el código ALI-006." in valido.text


def test_editar_precio_no_cambia_pedidos_confirmados(pedido, personal, servicios):
    pagina = personal.post(
        f"/personal/menu/{CAFE}",
        data={"nombre": "Café pasado", "categoria": "BEBIDA", "precio": "0,95", "disponible": "1"},
    )
    assert "Se guardaron los cambios de Café pasado." in pagina.text
    assert servicios.menu.obtener(CAFE).precio == Decimal("0.95")
    assert servicios.pedidos.obtener(pedido.id).total == Decimal("1.50")


def test_cambiar_disponibilidad_se_refleja_en_el_menu(personal, navegador):
    personal.post(f"/personal/menu/{HUMITA}/disponibilidad", data={"disponible": "1"})
    registrar(navegador)
    assert f'name="cant-{HUMITA}"' in navegador.get("/").text
    personal.post(f"/personal/menu/{HUMITA}/disponibilidad", data={"disponible": "0"})
    assert f'name="cant-{HUMITA}"' not in navegador.get("/").text


def test_editar_producto_inexistente_responde_404(personal):
    assert personal.get("/personal/menu/ALI-999").status_code == 404


def test_salir_del_personal(personal):
    personal.post("/personal/salir")
    assert personal.get("/personal").url.path == "/personal/ingresar"
