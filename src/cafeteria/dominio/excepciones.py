"""Excepciones de negocio de la cafetería.

Cada excepción representa una regla de negocio o una validación que no se cumple.
El atributo ``mensaje`` está redactado para mostrarse directamente al usuario.
"""


class ErrorDeNegocio(Exception):
    """Base de los errores que la aplicación muestra al usuario.

    Args:
        mensaje: explicación de qué falló y cómo corregirlo.
    """

    mensaje_por_defecto = "La operación no cumple las reglas de la cafetería."

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.mensaje_por_defecto
        super().__init__(self.mensaje)


class DatoInvalido(ErrorDeNegocio):
    """Un dato ingresado no tiene el formato o el rango esperado."""


class PedidoVacio(ErrorDeNegocio):
    """El pedido no incluye ningún producto (RN-NEG-01)."""

    mensaje_por_defecto = "El pedido debe incluir al menos un producto."


class CantidadInvalida(ErrorDeNegocio):
    """Una cantidad no es un entero positivo o supera el máximo (RN-NEG-01, supuesto A7)."""


class ProductoNoDisponible(ErrorDeNegocio):
    """Se intentó pedir un producto marcado como no disponible (RN-NEG-02).

    Args:
        nombre: nombre del producto no disponible.
    """

    def __init__(self, nombre: str) -> None:
        super().__init__(f"{nombre} ya no está disponible. Quítalo del pedido para continuar.")


class ProductoNoEncontrado(ErrorDeNegocio):
    """No existe un producto con el código indicado."""

    mensaje_por_defecto = "El producto no existe en el menú."


class TransicionNoPermitida(ErrorDeNegocio):
    """El cambio de estado del pedido viola el orden de RN-NEG-06 o RN-NEG-07."""


class CodigoRetiroIncorrecto(ErrorDeNegocio):
    """El código presentado no coincide con el del pedido (RN-NEG-07)."""

    mensaje_por_defecto = (
        "El código no coincide con este pedido. Verifícalo con el cliente; "
        "el pedido sigue en Listo para retirar."
    )


class CodigoRetiroDuplicado(ErrorDeNegocio):
    """El código de retiro generado ya existe; el servicio genera otro (RN-NEG-05)."""


class ClienteDuplicado(ErrorDeNegocio):
    """Ya existe un cliente con la misma cédula o el mismo correo."""


class CredencialesInvalidas(ErrorDeNegocio):
    """Los datos de ingreso no corresponden a ningún usuario registrado."""


class PedidoNoEncontrado(ErrorDeNegocio):
    """No existe un pedido con el identificador o código indicado."""

    mensaje_por_defecto = "No encontramos ese pedido."
