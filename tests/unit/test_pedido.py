"""Pruebas unitarias de las reglas de negocio del pedido (RN-NEG-01 a RN-NEG-07)."""

from datetime import datetime
from decimal import Decimal

import pytest

from cafeteria.dominio import excepciones as exc
from cafeteria.dominio.modelos import (
    CANTIDAD_MAXIMA_POR_PRODUCTO,
    ZONA_ECUADOR,
    Categoria,
    EstadoPedido,
    Pedido,
    Producto,
    validar_precio,
)

MOMENTO = datetime(2026, 11, 24, 10, 42, tzinfo=ZONA_ECUADOR)


@pytest.fixture
def bolon():
    return Producto("ALI-001", "Bolón de verde con queso", Categoria.ALIMENTO, Decimal("1.75"))


@pytest.fixture
def empanada():
    return Producto("ALI-002", "Empanada de viento", Categoria.ALIMENTO, Decimal("0.80"))


@pytest.fixture
def cafe():
    return Producto("BEB-001", "Café pasado", Categoria.BEBIDA, Decimal("0.75"))


def nuevo_pedido(*seleccion):
    return Pedido.confirmar(
        cliente_id=1, seleccion=list(seleccion), codigo_retiro="K7P-4QX", momento=MOMENTO
    )


# RN-NEG-01: al menos un producto y cantidades enteras positivas
def test_pedido_sin_productos_no_se_confirma():
    with pytest.raises(exc.PedidoVacio):
        nuevo_pedido()


@pytest.mark.parametrize("cantidad", [0, -1, 1.5, "2", True, None])
def test_cantidad_no_entera_positiva_se_rechaza(bolon, cantidad):
    with pytest.raises(exc.CantidadInvalida):
        nuevo_pedido((bolon, cantidad))


@pytest.mark.parametrize("cantidad", [1, CANTIDAD_MAXIMA_POR_PRODUCTO])
def test_cantidades_limite_validas_se_aceptan(bolon, cantidad):
    assert nuevo_pedido((bolon, cantidad)).detalles[0].cantidad == cantidad


def test_cantidad_mayor_al_maximo_se_rechaza(bolon):
    with pytest.raises(exc.CantidadInvalida):
        nuevo_pedido((bolon, CANTIDAD_MAXIMA_POR_PRODUCTO + 1))


# RN-NEG-02: solo productos disponibles
def test_producto_no_disponible_no_se_puede_pedir(bolon, cafe):
    cafe.disponible = False
    with pytest.raises(exc.ProductoNoDisponible):
        nuevo_pedido((bolon, 1), (cafe, 1))


# RN-NEG-03: total = suma de precio × cantidad
def test_total_es_la_suma_de_precio_por_cantidad(bolon, empanada, cafe):
    pedido = nuevo_pedido((bolon, 1), (empanada, 2), (cafe, 1))
    assert pedido.total == Decimal("4.10")
    assert pedido.cantidad_articulos == 4


# RN-NEG-04: el precio del pedido no cambia si cambia el menú
def test_precio_del_detalle_no_cambia_al_modificar_el_menu(empanada):
    pedido = nuevo_pedido((empanada, 2))
    empanada.actualizar(
        nombre=empanada.nombre, categoria=empanada.categoria, precio="1.00", disponible=True
    )
    assert pedido.detalles[0].precio_unitario == Decimal("0.80")
    assert pedido.total == Decimal("1.60")


# RN-NEG-06: inicia en Pendiente y avanza en orden
def test_pedido_confirmado_inicia_pendiente(bolon):
    pedido = nuevo_pedido((bolon, 1))
    assert pedido.estado is EstadoPedido.PENDIENTE
    assert pedido.fecha_registro == MOMENTO


def test_pedido_avanza_en_orden(bolon):
    pedido = nuevo_pedido((bolon, 1))
    pedido.avanzar(MOMENTO)
    assert pedido.estado is EstadoPedido.EN_PREPARACION
    pedido.avanzar(MOMENTO)
    assert pedido.estado is EstadoPedido.LISTO_PARA_RETIRAR
    assert pedido.fecha_listo == MOMENTO


# RN-NEG-07: entregado solo desde Listo y con el código correcto
def test_listo_no_avanza_sin_codigo(bolon):
    pedido = nuevo_pedido((bolon, 1))
    pedido.avanzar()
    pedido.avanzar()
    with pytest.raises(exc.TransicionNoPermitida):
        pedido.avanzar()


@pytest.mark.parametrize("pasos", [0, 1])
def test_no_se_entrega_si_no_esta_listo(bolon, pasos):
    pedido = nuevo_pedido((bolon, 1))
    for _ in range(pasos):
        pedido.avanzar()
    with pytest.raises(exc.TransicionNoPermitida):
        pedido.entregar("K7P-4QX")


def test_no_se_entrega_con_codigo_incorrecto(bolon):
    pedido = nuevo_pedido((bolon, 1))
    pedido.avanzar()
    pedido.avanzar()
    with pytest.raises(exc.CodigoRetiroIncorrecto):
        pedido.entregar("K7P-4QZ")
    assert pedido.estado is EstadoPedido.LISTO_PARA_RETIRAR


@pytest.mark.parametrize("escrito", ["K7P-4QX", "k7p4qx", " k7p-4qx "])
def test_se_entrega_con_codigo_correcto(bolon, escrito):
    pedido = nuevo_pedido((bolon, 1))
    pedido.avanzar()
    pedido.avanzar()
    pedido.entregar(escrito, MOMENTO)
    assert pedido.estado is EstadoPedido.ENTREGADO
    assert pedido.fecha_entrega == MOMENTO


def test_entregado_no_puede_cambiar(bolon):
    pedido = nuevo_pedido((bolon, 1))
    pedido.avanzar()
    pedido.avanzar()
    pedido.entregar("K7P-4QX")
    with pytest.raises(exc.TransicionNoPermitida):
        pedido.avanzar()


# Supuesto A6: precio en dólares, mayor que cero, dos decimales
@pytest.mark.parametrize("valor, esperado", [("1,50", "1.50"), ("2", "2.00"), ("0.01", "0.01")])
def test_precio_valido_se_normaliza(valor, esperado):
    assert validar_precio(valor) == Decimal(esperado)


@pytest.mark.parametrize("valor", ["0", "-1", "1.505", "abc", "NaN", "100.01"])
def test_precio_invalido_se_rechaza(valor):
    with pytest.raises(exc.DatoInvalido):
        validar_precio(valor)
