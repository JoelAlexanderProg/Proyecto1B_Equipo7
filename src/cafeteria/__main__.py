"""Arranque de CaféPoli: ``python -m cafeteria`` o el comando ``cafepoli``.

Lee el archivo ``.env`` de la carpeta actual, si existe, y levanta el servidor Uvicorn.
``CAFETERIA_HOST`` y ``CAFETERIA_PUERTO`` cambian la dirección (por defecto
``127.0.0.1:8000``).
"""

import os

import uvicorn

from cafeteria.config import cargar_archivo_env


def main() -> None:
    """Carga la configuración del entorno y ejecuta la aplicación."""
    cargar_archivo_env(".env")
    uvicorn.run(
        "cafeteria.presentacion.web:crear_app",
        factory=True,
        host=os.environ.get("CAFETERIA_HOST", "127.0.0.1"),
        port=int(os.environ.get("CAFETERIA_PUERTO", "8000")),
    )


if __name__ == "__main__":
    main()
