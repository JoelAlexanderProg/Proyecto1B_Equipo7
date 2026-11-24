"""Validación de los datos del cliente (supuesto A2).

Las funciones devuelven el dato normalizado o lanzan ``DatoInvalido`` con un mensaje
que explica cómo corregirlo.
"""

import re

from cafeteria.dominio.excepciones import DatoInvalido

_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]{2,40}$")
_PATRON_CELULAR = re.compile(r"^09\d{8}$")
_PATRON_USUARIO_CORREO = re.compile(r"^[a-z0-9._%+-]+$")
_COEFICIENTES_CEDULA = (2, 1, 2, 1, 2, 1, 2, 1, 2)
_PROVINCIAS_VALIDAS = set(range(1, 25)) | {30}


def validar_nombre_persona(valor: str, campo: str) -> str:
    """Valida un nombre o apellido.

    Args:
        valor: texto ingresado.
        campo: nombre del campo para el mensaje de error ("nombre" o "apellido").

    Returns:
        str: el valor sin espacios sobrantes.

    Raises:
        DatoInvalido: si está vacío, es muy corto o contiene números o símbolos.
    """
    limpio = " ".join(valor.split())
    if not _PATRON_NOMBRE.fullmatch(limpio):
        raise DatoInvalido(f"Escribe un {campo} válido: solo letras, entre 2 y 40 caracteres.")
    return limpio


def validar_cedula(valor: str) -> str:
    """Valida una cédula ecuatoriana con su dígito verificador (algoritmo módulo 10).

    Los dos primeros dígitos son la provincia (01 a 24, o 30 para ecuatorianos en el
    exterior), el tercero es menor que 6 y el décimo se calcula con los coeficientes
    2, 1, 2, 1... sobre los nueve primeros.

    Args:
        valor: cédula ingresada.

    Returns:
        str: la cédula de 10 dígitos.

    Raises:
        DatoInvalido: si no tiene 10 dígitos o el dígito verificador no coincide.
    """
    cedula = valor.strip()
    if len(cedula) != 10 or not cedula.isdigit():
        raise DatoInvalido("La cédula debe tener 10 dígitos.")
    if int(cedula[:2]) not in _PROVINCIAS_VALIDAS or int(cedula[2]) >= 6:
        raise DatoInvalido("La cédula no es válida. Revisa los dígitos.")
    suma = 0
    for digito, coeficiente in zip(cedula[:9], _COEFICIENTES_CEDULA, strict=True):
        producto = int(digito) * coeficiente
        suma += producto - 9 if producto > 9 else producto
    verificador = (10 - suma % 10) % 10
    if verificador != int(cedula[9]):
        raise DatoInvalido("La cédula no es válida. Revisa los dígitos.")
    return cedula


def validar_celular(valor: str) -> str:
    """Valida un número de celular ecuatoriano (09 seguido de 8 dígitos).

    Args:
        valor: número ingresado; se aceptan espacios y guiones.

    Returns:
        str: el número de 10 dígitos sin separadores.

    Raises:
        DatoInvalido: si no tiene el formato 09XXXXXXXX.
    """
    celular = re.sub(r"[\s-]", "", valor)
    if not _PATRON_CELULAR.fullmatch(celular):
        raise DatoInvalido("El celular debe tener 10 dígitos y empezar con 09.")
    return celular


def validar_correo_institucional(valor: str, dominio: str) -> str:
    """Valida que el correo pertenezca al dominio de la institución.

    Args:
        valor: correo ingresado.
        dominio: dominio institucional permitido, por ejemplo ``epn.edu.ec``.

    Returns:
        str: el correo en minúsculas.

    Raises:
        DatoInvalido: si el correo no es del dominio institucional.
    """
    correo = valor.strip().lower()
    usuario, separador, dominio_correo = correo.partition("@")
    if not separador or dominio_correo != dominio.lower() or not _PATRON_USUARIO_CORREO.fullmatch(
        usuario
    ):
        raise DatoInvalido(f"Usa tu correo institucional (usuario@{dominio}).")
    return correo
