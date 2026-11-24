"""Configuración de la aplicación leída de variables de entorno.

Las variables de entorno separan la configuración del código. No son un almacén
seguro de secretos: la clave del personal se define en un archivo ``.env`` que no se
sube al repositorio (``.env.example`` documenta cada variable sin valores reales).
"""

import os
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class ConfiguracionInvalida(RuntimeError):
    """Falta una variable de entorno obligatoria o tiene un valor no válido."""


def cargar_archivo_env(ruta: str | Path = ".env") -> None:
    """Carga las variables de un archivo ``CLAVE=valor`` sin sobrescribir las existentes.

    Las líneas vacías y las que empiezan con ``#`` se ignoran. Si el archivo no existe,
    no hace nada.

    Args:
        ruta: ruta del archivo de variables.
    """
    archivo = Path(ruta)
    if not archivo.is_file():
        return
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def _booleano(valor: str) -> bool:
    return valor.strip().lower() in {"1", "true", "si", "sí", "yes"}


@dataclass(frozen=True)
class Configuracion:
    """Parámetros de ejecución de la aplicación.

    Attributes:
        ruta_bd: archivo SQLite.
        usuario_personal: usuario de la cuenta del personal (supuesto A4).
        clave_personal: clave de la cuenta del personal.
        secreto_sesion: clave con la que se firman las cookies de sesión.
        dominio_correo: dominio del correo institucional de los clientes.
        cargar_semilla: si se carga el menú de demostración cuando la base está vacía.
    """

    ruta_bd: Path
    usuario_personal: str
    clave_personal: str
    secreto_sesion: str
    dominio_correo: str = "epn.edu.ec"
    cargar_semilla: bool = True

    @classmethod
    def desde_entorno(cls, entorno: Mapping[str, str] | None = None) -> "Configuracion":
        """Construye la configuración desde las variables ``CAFETERIA_*``.

        Args:
            entorno: variables a usar; por defecto, ``os.environ``.

        Returns:
            Configuracion: la configuración validada.

        Raises:
            ConfiguracionInvalida: si falta la clave del personal o es muy corta.
        """
        env = os.environ if entorno is None else entorno
        clave = env.get("CAFETERIA_CLAVE_PERSONAL", "")
        if len(clave) < 8:
            raise ConfiguracionInvalida(
                "Define CAFETERIA_CLAVE_PERSONAL con al menos 8 caracteres "
                "(copia .env.example como .env y edítalo)."
            )
        return cls(
            ruta_bd=Path(env.get("CAFETERIA_BD", "data/cafeteria.db")),
            usuario_personal=env.get("CAFETERIA_USUARIO_PERSONAL", "personal"),
            clave_personal=clave,
            secreto_sesion=env.get("CAFETERIA_SECRETO_SESION") or secrets.token_urlsafe(32),
            dominio_correo=env.get("CAFETERIA_DOMINIO_CORREO", "epn.edu.ec"),
            cargar_semilla=_booleano(env.get("CAFETERIA_CARGAR_SEMILLA", "1")),
        )
