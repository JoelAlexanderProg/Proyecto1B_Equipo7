"""Fábrica de la aplicación FastAPI: arma las capas y registra las rutas.

Ejecución local: ``python -m cafeteria`` (lee ``.env``) o
``uvicorn cafeteria.presentacion.web:crear_app --factory``.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from cafeteria import __version__
from cafeteria.aplicacion.servicios import (
    ServicioAccesoPersonal,
    ServicioClientes,
    ServicioMenu,
    ServicioPedidos,
)
from cafeteria.config import Configuracion
from cafeteria.dominio.excepciones import ErrorDeNegocio
from cafeteria.infraestructura.basedatos import BaseDatos
from cafeteria.infraestructura.repositorios import (
    RepositorioClientesSQLite,
    RepositorioPedidosSQLite,
    RepositorioProductosSQLite,
)
from cafeteria.infraestructura.semilla import cargar_menu_inicial
from cafeteria.presentacion import rutas_api, rutas_cliente
from cafeteria.presentacion.dependencias import Servicios
from cafeteria.presentacion.plantillas import mostrar

DURACION_SESION = 8 * 60 * 60
"""Una jornada de la cafetería, en segundos."""


def crear_servicios(config: Configuracion) -> Servicios:
    """Crea la base de datos y conecta cada servicio con sus repositorios.

    Args:
        config: configuración de la aplicación.

    Returns:
        Servicios: los servicios listos para usar.
    """
    bd = BaseDatos(config.ruta_bd)
    bd.crear_esquema()
    productos = RepositorioProductosSQLite(bd)
    servicios = Servicios(
        menu=ServicioMenu(productos),
        clientes=ServicioClientes(RepositorioClientesSQLite(bd), config.dominio_correo),
        pedidos=ServicioPedidos(RepositorioPedidosSQLite(bd), productos),
        acceso=ServicioAccesoPersonal(config.usuario_personal, config.clave_personal),
    )
    if config.cargar_semilla:
        cargar_menu_inicial(servicios.menu)
    return servicios


def crear_app(config: Configuracion | None = None) -> FastAPI:
    """Crea la aplicación web.

    Args:
        config: configuración; por defecto se lee de las variables de entorno.

    Returns:
        FastAPI: la aplicación con sus rutas, archivos estáticos y sesión.
    """
    config = config or Configuracion.desde_entorno()
    app = FastAPI(
        title="CaféPoli",
        version=__version__,
        description=(
            "Pedidos anticipados, seguimiento y retiro con código para la cafetería "
            "universitaria. Las páginas web usan sesión; la API expone el menú y el "
            "estado del servicio."
        ),
    )
    app.state.servicios = crear_servicios(config)
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.secreto_sesion,
        session_cookie="cafepoli_sesion",
        max_age=DURACION_SESION,
        same_site="lax",
    )
    app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
    app.include_router(rutas_cliente.router)
    app.include_router(rutas_api.router)

    @app.exception_handler(StarletteHTTPException)
    async def pagina_de_error(request: Request, error: StarletteHTTPException):
        if request.url.path.startswith("/api/"):
            return JSONResponse({"detail": error.detail}, status_code=error.status_code)
        mensaje = "No encontramos esa página." if error.status_code == 404 else error.detail
        return mostrar(request, "error.html", {"mensaje": mensaje}, status_code=error.status_code)

    @app.exception_handler(ErrorDeNegocio)
    async def error_de_negocio(request: Request, error: ErrorDeNegocio):
        return mostrar(request, "error.html", {"mensaje": error.mensaje}, status_code=400)

    return app
