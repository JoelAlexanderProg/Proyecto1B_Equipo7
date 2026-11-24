"""Pruebas de integración: servicios de aplicación con una base SQLite real temporal."""

from datetime import datetime
from decimal import Decimal

import pytest

from cafeteria.aplicacion.servicios import (
    ServicioAccesoPersonal,
    ServicioClientes,
    ServicioMenu,
    ServicioPedidos,
)
from cafeteria.dominio import excepciones as exc
from cafeteria.dominio.codigo_retiro import es_codigo_valido
from cafeteria.dominio.modelos import ZONA_ECUADOR, EstadoPedido
from cafeteria.infraestructura.basedatos import BaseDatos
from cafeteria.infraestructura.repositorios import (
    RepositorioClientesSQLite,
    RepositorioPedidosSQLite,
    RepositorioProductosSQLite,
)
from cafeteria.infraestructura.semilla import MENU_INICIAL, cargar_menu_inicial

AHORA = datetime(2026, 11, 24, 10, 42, tzinfo=ZONA_ECUADOR)


class Sistema:
    """Arma los servicios sobre una base de datos en un archivo."""

    def __init__(self, ruta, generar_codigo=None):
        self.bd = BaseDatos(ruta)
        self.bd.crear_esquema()
        productos = RepositorioProductosSQLite(self.bd)
        self.repo_pedidos = RepositorioPedidosSQLite(self.bd)
        self.menu = ServicioMenu(productos)
        self.clientes = ServicioClientes(RepositorioClientesSQLite(self.bd), "epn.edu.ec")
        opciones = {"reloj": lambda: AHORA}
        if generar_codigo:
            opciones["generar_codigo"] = generar_codigo
        self.pedidos = ServicioPedidos(self.repo_pedidos, productos, **opciones)


@pytest.fixture
def sistema(tmp_path):
    s = Sistema(tmp_path / "cafeteria.db")
    cargar_menu_inicial(s.menu)
    return s


@pytest.fixture
def ana(sistema):
    return sistema.clientes.registrar(
        nombre="Ana",
        apellido="Pérez",
        cedula="1710034065",
        celular="0991234567",
        correo="ana.perez@epn.edu.ec",
    )


def codigo_de(sistema, nombre):
    return next(p.codigo for p in sistema.menu.listar() if p.nombre == nombre)


def test_semilla_carga_el_menu_una_sola_vez(sistema):
    assert len(sistema.menu.listar()) == len(MENU_INICIAL)
    assert cargar_menu_inicial(sistema.menu) == 0


def test_codigos_de_producto_por_categoria(sistema):
    nuevo = sistema.menu.registrar(
        nombre="Tigrillo", categoria="ALIMENTO", precio="2,50", disponible=True
    )
    assert nuevo.codigo == "ALI-006"
    assert nuevo.precio == Decimal("2.50")


def test_menu_solo_disponibles_excluye_no_disponibles(sistema):
    nombres = [p.nombre for p in sistema.menu.listar(solo_disponibles=True)]
    assert "Humita" not in nombres


def test_confirmar_pedido_persiste_pendiente_con_codigo(sistema, ana):
    cantidades = {
        codigo_de(sistema, "Bolón de verde con queso"): 1,
        codigo_de(sistema, "Empanada de viento"): 2,
    }
    pedido = sistema.pedidos.confirmar(ana.id, cantidades)
    guardado = sistema.pedidos.obtener_por_codigo(pedido.codigo_retiro)
    assert es_codigo_valido(guardado.codigo_retiro)
    assert guardado.estado is EstadoPedido.PENDIENTE
    assert guardado.total == Decimal("3.35")
    assert guardado.fecha_registro == AHORA


def test_revisar_calcula_total_sin_guardar(sistema, ana):
    _, total = sistema.pedidos.revisar({codigo_de(sistema, "Café pasado"): 3})
    assert total == Decimal("2.25")
    assert sistema.pedidos.pedidos_de_cliente(ana.id) == []


def test_producto_no_disponible_no_se_confirma(sistema, ana):
    with pytest.raises(exc.ProductoNoDisponible):
        sistema.pedidos.confirmar(ana.id, {codigo_de(sistema, "Humita"): 1})
    assert sistema.pedidos.pedidos_de_cliente(ana.id) == []


def test_producto_inexistente_no_se_confirma(sistema, ana):
    with pytest.raises(exc.ProductoNoEncontrado):
        sistema.pedidos.confirmar(ana.id, {"ALI-999": 1})


def test_precio_del_pedido_guardado_no_cambia_con_el_menu(sistema, ana):
    codigo = codigo_de(sistema, "Empanada de viento")
    pedido = sistema.pedidos.confirmar(ana.id, {codigo: 2})
    sistema.menu.actualizar(
        codigo, nombre="Empanada de viento", categoria="ALIMENTO", precio="1.10", disponible=True
    )
    guardado = sistema.pedidos.obtener(pedido.id)
    assert guardado.detalles[0].precio_unitario == Decimal("0.80")
    assert guardado.total == Decimal("1.60")


def test_codigo_duplicado_se_regenera(tmp_path):
    codigos = iter(["AAA-AAA", "AAA-AAA", "BBB-BBB"])
    s = Sistema(tmp_path / "c.db", generar_codigo=lambda: next(codigos))
    cargar_menu_inicial(s.menu)
    cliente = s.clientes.registrar(
        nombre="Luis",
        apellido="Cruz",
        cedula="0102030400",
        celular="0987654321",
        correo="luis.cruz@epn.edu.ec",
    )
    cafe = codigo_de(s, "Café pasado")
    primero = s.pedidos.confirmar(cliente.id, {cafe: 1})
    segundo = s.pedidos.confirmar(cliente.id, {cafe: 1})
    assert (primero.codigo_retiro, segundo.codigo_retiro) == ("AAA-AAA", "BBB-BBB")


def test_flujo_de_preparacion_y_entrega(sistema, ana):
    pedido = sistema.pedidos.confirmar(ana.id, {codigo_de(sistema, "Capuchino"): 1})
    assert sistema.pedidos.tablero()[EstadoPedido.PENDIENTE][0].id == pedido.id
    sistema.pedidos.avanzar(pedido.id)
    sistema.pedidos.avanzar(pedido.id)
    with pytest.raises(exc.CodigoRetiroIncorrecto):
        sistema.pedidos.entregar(pedido.id, "ZZZ-ZZZ")
    entregado = sistema.pedidos.entregar(pedido.id, pedido.codigo_retiro.lower())
    assert entregado.estado is EstadoPedido.ENTREGADO
    assert sistema.pedidos.obtener(pedido.id).fecha_entrega == AHORA
    assert sistema.pedidos.entregados_hoy() == 1
    assert all(not columna for columna in sistema.pedidos.tablero().values())


def test_cambio_simultaneo_de_estado_se_detecta(sistema, ana):
    pedido = sistema.pedidos.confirmar(ana.id, {codigo_de(sistema, "Capuchino"): 1})
    copia_a = sistema.repo_pedidos.obtener(pedido.id)
    copia_b = sistema.repo_pedidos.obtener(pedido.id)
    copia_a.avanzar(AHORA)
    sistema.repo_pedidos.actualizar_estado(copia_a, EstadoPedido.PENDIENTE)
    copia_b.avanzar(AHORA)
    with pytest.raises(exc.TransicionNoPermitida):
        sistema.repo_pedidos.actualizar_estado(copia_b, EstadoPedido.PENDIENTE)


def test_los_datos_persisten_entre_ejecuciones(tmp_path):
    ruta = tmp_path / "persistente.db"
    primera = Sistema(ruta)
    cargar_menu_inicial(primera.menu)
    cliente = primera.clientes.registrar(
        nombre="Sofía",
        apellido="Mena",
        cedula="1710034065",
        celular="0991112233",
        correo="sofia.mena@epn.edu.ec",
    )
    pedido = primera.pedidos.confirmar(cliente.id, {codigo_de(primera, "Agua sin gas"): 2})
    segunda = Sistema(ruta)
    assert segunda.pedidos.obtener_por_codigo(pedido.codigo_retiro).total == Decimal("1.20")
    assert len(segunda.menu.listar()) == len(MENU_INICIAL)


def test_registro_asigna_codigo_de_cliente(ana):
    assert ana.codigo == "CLI-0001"


@pytest.mark.parametrize(
    "cedula, correo",
    [("1710034065", "otra@epn.edu.ec"), ("0102030400", "ana.perez@epn.edu.ec")],
)
def test_cliente_duplicado_se_rechaza(sistema, ana, cedula, correo):
    with pytest.raises(exc.ClienteDuplicado):
        sistema.clientes.registrar(
            nombre="Ana", apellido="Pérez", cedula=cedula, celular="0991234567", correo=correo
        )


def test_identificar_cliente(sistema, ana):
    assert sistema.clientes.identificar(correo=" ANA.perez@epn.edu.ec", cedula="1710034065") == ana
    with pytest.raises(exc.CredencialesInvalidas):
        sistema.clientes.identificar(correo="ana.perez@epn.edu.ec", cedula="0102030400")


def test_acceso_del_personal():
    acceso = ServicioAccesoPersonal("personal", "clave-segura")
    acceso.verificar("personal", "clave-segura")
    with pytest.raises(exc.CredencialesInvalidas):
        acceso.verificar("personal", "otra")
