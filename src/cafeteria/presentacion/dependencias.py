"""Acceso de las rutas a los servicios de aplicación y a la sesión."""

from dataclasses import dataclass

from fastapi import Request

from cafeteria.aplicacion.servicios import (
    ServicioAccesoPersonal,
    ServicioClientes,
    ServicioMenu,
    ServicioPedidos,
)
from cafeteria.dominio.modelos import Cliente


@dataclass(frozen=True)
class Servicios:
    """Servicios de aplicación compartidos por todas las rutas."""

    menu: ServicioMenu
    clientes: ServicioClientes
    pedidos: ServicioPedidos
    acceso: ServicioAccesoPersonal


def servicios(request: Request) -> Servicios:
    """Devuelve los servicios de la aplicación desde una petición."""
    return request.app.state.servicios


def cliente_actual(request: Request) -> Cliente | None:
    """Devuelve el cliente identificado en la sesión, o None."""
    cliente_id = request.session.get("cliente_id")
    return servicios(request).clientes.obtener(cliente_id) if cliente_id else None


def es_personal(request: Request) -> bool:
    """Indica si la sesión pertenece al personal de la cafetería."""
    return request.session.get("personal") is True
