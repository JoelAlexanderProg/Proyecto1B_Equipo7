"""API JSON: estado del servicio (healthcheck) y consulta del menú."""

from decimal import Decimal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from cafeteria import __version__
from cafeteria.presentacion.dependencias import servicios

router = APIRouter()


class EstadoServicio(BaseModel):
    """Respuesta del healthcheck."""

    estado: str
    version: str


class ProductoSalida(BaseModel):
    """Producto del menú tal como lo expone la API."""

    codigo: str
    nombre: str
    categoria: str
    precio: Decimal
    disponible: bool


@router.get("/health", tags=["operación"])
def salud() -> EstadoServicio:
    """Indica que la aplicación responde; lo usa el HEALTHCHECK de Docker."""
    return EstadoServicio(estado="ok", version=__version__)


@router.get("/api/v1/productos", tags=["menú"])
def listar_productos(request: Request, disponibles: bool = False) -> list[ProductoSalida]:
    """Devuelve el menú ordenado por categoría y nombre (RU-01).

    - **disponibles**: si es `true`, solo devuelve los productos que se pueden pedir.
    """
    productos = servicios(request).menu.listar(solo_disponibles=disponibles)
    return [
        ProductoSalida(
            codigo=p.codigo,
            nombre=p.nombre,
            categoria=p.categoria.value,
            precio=p.precio,
            disponible=p.disponible,
        )
        for p in productos
    ]
