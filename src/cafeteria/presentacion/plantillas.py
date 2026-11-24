"""Motor de plantillas Jinja2, filtros de formato y utilidades comunes de las páginas."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from cafeteria import __version__
from cafeteria.dominio.modelos import CANTIDAD_MAXIMA_POR_PRODUCTO, EstadoPedido

plantillas = Jinja2Templates(directory=Path(__file__).parent / "templates")


def formatear_dinero(valor: Decimal) -> str:
    """Formatea un monto en dólares con coma decimal, como se usa en Ecuador: ``$4,10``."""
    return f"${valor:.2f}".replace(".", ",")


def formatear_hora(fecha: datetime | None) -> str:
    """Devuelve la hora ``HH:MM`` o una raya si la fecha no existe."""
    return fecha.strftime("%H:%M") if fecha else "—"


def formatear_fecha(fecha: datetime | None) -> str:
    """Devuelve la fecha ``dd/mm/aaaa HH:MM`` o una raya si la fecha no existe."""
    return fecha.strftime("%d/%m/%Y %H:%M") if fecha else "—"


plantillas.env.filters.update(dinero=formatear_dinero, hora=formatear_hora, fecha=formatear_fecha)
plantillas.env.globals.update(
    EstadoPedido=EstadoPedido,
    CANTIDAD_MAXIMA=CANTIDAD_MAXIMA_POR_PRODUCTO,
    VERSION=__version__,
)


def avisar(request: Request, texto: str, tipo: str = "ok") -> None:
    """Guarda un aviso en la sesión para mostrarlo en la siguiente página.

    Args:
        request: petición actual.
        texto: mensaje para el usuario.
        tipo: ``ok`` o ``error``; define el color del aviso.
    """
    request.session["aviso"] = {"texto": texto, "tipo": tipo}


def mostrar(
    request: Request, plantilla: str, contexto: dict | None = None, status_code: int = 200
) -> HTMLResponse:
    """Renderiza una plantilla con el aviso pendiente de la sesión, si lo hay.

    Args:
        request: petición actual.
        plantilla: ruta de la plantilla dentro de ``templates``.
        contexto: variables para la plantilla.
        status_code: código HTTP de la respuesta.

    Returns:
        HTMLResponse: la página renderizada.
    """
    datos = {"aviso": request.session.pop("aviso", None), **(contexto or {})}
    return plantillas.TemplateResponse(request, plantilla, datos, status_code=status_code)


def redirigir(url: str) -> RedirectResponse:
    """Redirige con 303 para que el navegador pida la nueva página con GET (patrón PRG)."""
    return RedirectResponse(url, status_code=303)
