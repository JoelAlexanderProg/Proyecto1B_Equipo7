"""Generación y normalización del código de retiro (RN-NEG-05, RN-04, supuesto A3).

El código tiene seis caracteres agrupados de tres en tres (``K7P-4QX``). El alfabeto
excluye los caracteres que se confunden al leerlos o dictarlos en el mostrador:
0/O y 1/I/L. Con 31 símbolos hay 31^6 (unos 887 millones) de combinaciones; la
unicidad se garantiza además con una restricción UNIQUE en la base de datos.
"""

import secrets

ALFABETO = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
LONGITUD = 6


def generar_codigo_retiro() -> str:
    """Genera un código de retiro aleatorio con un generador criptográfico.

    Returns:
        str: código con el formato ``XXX-XXX``.
    """
    caracteres = "".join(secrets.choice(ALFABETO) for _ in range(LONGITUD))
    return f"{caracteres[:3]}-{caracteres[3:]}"


def normalizar_codigo_retiro(texto: str) -> str:
    """Convierte lo que escribe el personal al formato canónico del código.

    Acepta minúsculas, espacios y el guion opcional: ``" k7p4qx "`` → ``"K7P-4QX"``.

    Args:
        texto: código escrito por el usuario.

    Returns:
        str: el código en formato ``XXX-XXX`` si tiene seis caracteres; en otro caso,
        el texto limpio en mayúsculas (que no coincidirá con ningún pedido).
    """
    limpio = "".join(texto.split()).replace("-", "").upper()
    if len(limpio) == LONGITUD:
        return f"{limpio[:3]}-{limpio[3:]}"
    return limpio


def es_codigo_valido(texto: str) -> bool:
    """Indica si un texto, ya normalizado, tiene la forma de un código de retiro.

    Args:
        texto: código a verificar.

    Returns:
        bool: True si tiene el formato ``XXX-XXX`` con caracteres del alfabeto.
    """
    codigo = normalizar_codigo_retiro(texto)
    simbolos = codigo.replace("-", "")
    return (
        len(codigo) == LONGITUD + 1
        and codigo[3] == "-"
        and all(caracter in ALFABETO for caracter in simbolos)
    )
