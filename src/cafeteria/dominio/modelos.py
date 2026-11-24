"""Entidades del dominio y reglas de negocio de la cafetería.

Este módulo no depende de FastAPI ni de la base de datos. Concentra las reglas
RN-NEG-01 a RN-NEG-07 de la especificación del cliente (v1.0) para que se puedan
verificar con pruebas unitarias.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from cafeteria.dominio import excepciones as exc
from cafeteria.dominio.codigo_retiro import normalizar_codigo_retiro
from cafeteria.dominio.validaciones import (
    validar_cedula,
    validar_celular,
    validar_correo_institucional,
    validar_nombre_persona,
)

ZONA_ECUADOR = timezone(timedelta(hours=-5), "America/Guayaquil")
"""Ecuador continental no tiene horario de verano: UTC-05:00 todo el año (supuesto A11)."""

CANTIDAD_MAXIMA_POR_PRODUCTO = 20
"""Unidades máximas de un mismo producto en un pedido (supuesto A7)."""

PRECIO_MAXIMO = Decimal("100.00")
LONGITUD_MAXIMA_NOMBRE_PRODUCTO = 60
_CENTAVO = Decimal("0.01")


def ahora() -> datetime:
    """Devuelve la fecha y hora actual en la zona horaria de Ecuador."""
    return datetime.now(ZONA_ECUADOR)


class Categoria(StrEnum):
    """Tipo de producto del menú; la especificación menciona alimentos y bebidas."""

    ALIMENTO = "ALIMENTO"
    BEBIDA = "BEBIDA"

    @property
    def etiqueta(self) -> str:
        """Nombre legible para la interfaz."""
        return "Alimentos" if self is Categoria.ALIMENTO else "Bebidas"

    @property
    def prefijo(self) -> str:
        """Prefijo del código de producto: ``ALI-001`` o ``BEB-001`` (supuesto A5)."""
        return "ALI" if self is Categoria.ALIMENTO else "BEB"


class EstadoPedido(StrEnum):
    """Etapas de atención de un pedido, en el orden que fija RN-NEG-06."""

    PENDIENTE = "PENDIENTE"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO_PARA_RETIRAR = "LISTO_PARA_RETIRAR"
    ENTREGADO = "ENTREGADO"

    @property
    def etiqueta(self) -> str:
        """Nombre del estado tal como lo usa la especificación."""
        return _ETIQUETAS_ESTADO[self]

    @property
    def siguiente(self) -> EstadoPedido | None:
        """Único estado al que se puede avanzar, o None si es el último (RN-NEG-06)."""
        return _SIGUIENTE_ESTADO.get(self)


_ETIQUETAS_ESTADO = {
    EstadoPedido.PENDIENTE: "Pendiente",
    EstadoPedido.EN_PREPARACION: "En preparación",
    EstadoPedido.LISTO_PARA_RETIRAR: "Listo para retirar",
    EstadoPedido.ENTREGADO: "Entregado",
}

# Tabla de transiciones: reemplaza una cadena de if/elif (Decompose Conditional).
_SIGUIENTE_ESTADO = {
    EstadoPedido.PENDIENTE: EstadoPedido.EN_PREPARACION,
    EstadoPedido.EN_PREPARACION: EstadoPedido.LISTO_PARA_RETIRAR,
    EstadoPedido.LISTO_PARA_RETIRAR: EstadoPedido.ENTREGADO,
}


def validar_precio(valor: Decimal | str | int) -> Decimal:
    """Valida y normaliza un precio en dólares (supuesto A6).

    Se usa ``Decimal`` y nunca ``float`` para que los montos no tengan errores de
    redondeo binario.

    Args:
        valor: precio ingresado; acepta coma o punto decimal ("1,50" o "1.50").

    Returns:
        Decimal: el precio con dos decimales.

    Raises:
        DatoInvalido: si no es un número, tiene más de dos decimales, no es mayor que
            cero o supera el máximo permitido.
    """
    try:
        precio = Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation:
        raise exc.DatoInvalido("El precio debe ser un número, por ejemplo 1,50.") from None
    if not precio.is_finite():
        raise exc.DatoInvalido("El precio debe ser un número, por ejemplo 1,50.")
    if precio.as_tuple().exponent < -2:
        raise exc.DatoInvalido("El precio admite como máximo dos decimales.")
    if precio <= 0:
        raise exc.DatoInvalido("El precio debe ser mayor que cero.")
    if precio > PRECIO_MAXIMO:
        raise exc.DatoInvalido(f"El precio no puede superar ${PRECIO_MAXIMO}.")
    return precio.quantize(_CENTAVO)


def validar_nombre_producto(valor: str) -> str:
    """Valida el nombre de un producto del menú.

    Args:
        valor: nombre ingresado.

    Returns:
        str: el nombre sin espacios sobrantes.

    Raises:
        DatoInvalido: si está vacío o supera 60 caracteres.
    """
    nombre = " ".join(valor.split())
    if not nombre:
        raise exc.DatoInvalido("Escribe el nombre del producto.")
    if len(nombre) > LONGITUD_MAXIMA_NOMBRE_PRODUCTO:
        raise exc.DatoInvalido("El nombre del producto admite hasta 60 caracteres.")
    return nombre


def validar_cantidad(cantidad: int, nombre_producto: str) -> int:
    """Valida la cantidad pedida de un producto (RN-NEG-01, supuesto A7).

    Args:
        cantidad: unidades solicitadas.
        nombre_producto: nombre del producto, para el mensaje de error.

    Returns:
        int: la misma cantidad, si es válida.

    Raises:
        CantidadInvalida: si no es un entero, es menor que 1 o supera el máximo.
    """
    if isinstance(cantidad, bool) or not isinstance(cantidad, int):
        raise exc.CantidadInvalida(f"La cantidad de {nombre_producto} debe ser un número entero.")
    if cantidad < 1:
        raise exc.CantidadInvalida(f"La cantidad de {nombre_producto} debe ser mayor que cero.")
    if cantidad > CANTIDAD_MAXIMA_POR_PRODUCTO:
        raise exc.CantidadInvalida(
            f"Puedes pedir hasta {CANTIDAD_MAXIMA_POR_PRODUCTO} unidades de {nombre_producto}."
        )
    return cantidad


@dataclass
class Producto:
    """Artículo del menú, identificado por código, nombre, precio y disponibilidad.

    Attributes:
        codigo: identificador único, por ejemplo ``ALI-001``.
        nombre: nombre visible en el menú.
        categoria: alimento o bebida.
        precio: precio vigente en dólares.
        disponible: si se puede incluir en nuevos pedidos (RN-NEG-02).
        id: clave interna asignada por la base de datos.
    """

    codigo: str
    nombre: str
    categoria: Categoria
    precio: Decimal
    disponible: bool = True
    id: int | None = None

    def __post_init__(self) -> None:
        self.nombre = validar_nombre_producto(self.nombre)
        self.precio = validar_precio(self.precio)
        self.categoria = Categoria(self.categoria)

    def actualizar(
        self, *, nombre: str, categoria: Categoria, precio: Decimal | str, disponible: bool
    ) -> None:
        """Modifica los datos del producto validándolos antes de asignar cualquiera.

        Cambiar el precio no afecta los pedidos ya confirmados, porque cada detalle
        guarda su propio precio (RN-NEG-04).

        Args:
            nombre: nuevo nombre.
            categoria: nueva categoría.
            precio: nuevo precio vigente.
            disponible: nueva disponibilidad.

        Raises:
            DatoInvalido: si el nombre o el precio no son válidos.
        """
        nombre_valido = validar_nombre_producto(nombre)
        precio_valido = validar_precio(precio)
        self.nombre = nombre_valido
        self.precio = precio_valido
        self.categoria = Categoria(categoria)
        self.disponible = disponible


@dataclass(frozen=True)
class Cliente:
    """Estudiante o docente que registra pedidos.

    Es inmutable: los datos se validan una vez, al registrarse.

    Attributes:
        codigo: código de cliente asignado por el sistema, por ejemplo ``CLI-0001``.
        nombre: nombres.
        apellido: apellidos.
        cedula: cédula ecuatoriana de 10 dígitos.
        celular: celular de 10 dígitos.
        correo: correo institucional en minúsculas.
        id: clave interna asignada por la base de datos.
    """

    codigo: str
    nombre: str
    apellido: str
    cedula: str
    celular: str
    correo: str
    id: int | None = None

    @classmethod
    def nuevo(
        cls, *, nombre: str, apellido: str, cedula: str, celular: str, correo: str, dominio: str
    ) -> Cliente:
        """Crea un cliente validando sus datos (supuesto A2).

        El código queda vacío hasta que el repositorio lo asigna al guardarlo.

        Args:
            nombre: nombres.
            apellido: apellidos.
            cedula: cédula ecuatoriana.
            celular: celular ecuatoriano.
            correo: correo institucional.
            dominio: dominio institucional permitido para el correo.

        Returns:
            Cliente: cliente con los datos normalizados.

        Raises:
            DatoInvalido: si algún dato no es válido.
        """
        return cls(
            codigo="",
            nombre=validar_nombre_persona(nombre, "nombre"),
            apellido=validar_nombre_persona(apellido, "apellido"),
            cedula=validar_cedula(cedula),
            celular=validar_celular(celular),
            correo=validar_correo_institucional(correo, dominio),
        )

    @property
    def nombre_corto(self) -> str:
        """Primer nombre e inicial del apellido, por ejemplo ``Ana P.``."""
        return f"{self.nombre.split()[0]} {self.apellido[0]}."

    @property
    def iniciales(self) -> str:
        """Iniciales del nombre y del apellido, por ejemplo ``AP``."""
        return f"{self.nombre[0]}{self.apellido[0]}".upper()

    def con_identidad(self, cliente_id: int, codigo: str) -> Cliente:
        """Devuelve el mismo cliente con el id y el código asignados al guardarlo.

        Args:
            cliente_id: clave asignada por la base de datos.
            codigo: código de cliente, por ejemplo ``CLI-0001``.

        Returns:
            Cliente: una copia con la identidad asignada; el original no cambia.
        """
        return Cliente(
            codigo=codigo,
            nombre=self.nombre,
            apellido=self.apellido,
            cedula=self.cedula,
            celular=self.celular,
            correo=self.correo,
            id=cliente_id,
        )


@dataclass(frozen=True)
class DetallePedido:
    """Producto incluido en un pedido, con su cantidad y el precio considerado.

    Es inmutable y no tiene métodos para cambiar el precio: el precio queda fijo al
    confirmar el pedido aunque después cambie en el menú (RN-NEG-04).

    Attributes:
        producto_codigo: código del producto.
        producto_nombre: nombre del producto al momento del pedido.
        cantidad: unidades solicitadas.
        precio_unitario: precio vigente al confirmar.
    """

    producto_codigo: str
    producto_nombre: str
    cantidad: int
    precio_unitario: Decimal

    @property
    def subtotal(self) -> Decimal:
        """Precio unitario por cantidad."""
        return (self.precio_unitario * self.cantidad).quantize(_CENTAVO)


def construir_detalles(seleccion: Iterable[tuple[Producto, int]]) -> tuple[DetallePedido, ...]:
    """Valida la selección del cliente y la convierte en detalles con el precio vigente.

    Aplica RN-NEG-01 (al menos un producto, cantidades enteras positivas), RN-NEG-02
    (solo productos disponibles) y RN-NEG-04 (se copia el precio vigente).

    Args:
        seleccion: pares (producto, cantidad).

    Returns:
        tuple[DetallePedido, ...]: un detalle por producto.

    Raises:
        PedidoVacio: si la selección está vacía.
        CantidadInvalida: si una cantidad no es válida.
        ProductoNoDisponible: si un producto no está disponible.
    """
    detalles = []
    for producto, cantidad in seleccion:
        validar_cantidad(cantidad, producto.nombre)
        if not producto.disponible:
            raise exc.ProductoNoDisponible(producto.nombre)
        detalles.append(
            DetallePedido(
                producto_codigo=producto.codigo,
                producto_nombre=producto.nombre,
                cantidad=cantidad,
                precio_unitario=producto.precio,
            )
        )
    if not detalles:
        raise exc.PedidoVacio()
    return tuple(detalles)


def calcular_total(detalles: Iterable[DetallePedido]) -> Decimal:
    """Suma el precio de cada producto multiplicado por su cantidad (RN-NEG-03).

    Args:
        detalles: detalles del pedido.

    Returns:
        Decimal: importe total con dos decimales.
    """
    return sum((detalle.subtotal for detalle in detalles), Decimal("0.00"))


@dataclass
class Pedido:
    """Solicitud confirmada por un cliente, con código de retiro, estado e importe.

    Attributes:
        codigo_retiro: código único para el retiro (RN-NEG-05).
        cliente_id: cliente que registró el pedido.
        detalles: productos, cantidades y precios considerados.
        estado: etapa de atención (RN-NEG-06).
        fecha_registro: momento de la confirmación.
        fecha_preparacion: momento en que pasó a En preparación.
        fecha_listo: momento en que pasó a Listo para retirar.
        fecha_entrega: momento de la entrega.
        id: clave interna asignada por la base de datos.
    """

    codigo_retiro: str
    cliente_id: int
    detalles: tuple[DetallePedido, ...]
    estado: EstadoPedido = EstadoPedido.PENDIENTE
    fecha_registro: datetime = field(default_factory=ahora)
    fecha_preparacion: datetime | None = None
    fecha_listo: datetime | None = None
    fecha_entrega: datetime | None = None
    id: int | None = None

    @classmethod
    def confirmar(
        cls,
        *,
        cliente_id: int,
        seleccion: Iterable[tuple[Producto, int]],
        codigo_retiro: str,
        momento: datetime | None = None,
    ) -> Pedido:
        """Registra un pedido confirmado en estado Pendiente (PN-01, RN-NEG-06).

        Args:
            cliente_id: cliente que confirma.
            seleccion: pares (producto, cantidad).
            codigo_retiro: código único generado para el pedido.
            momento: fecha de registro; por defecto, la hora actual.

        Returns:
            Pedido: el pedido en estado Pendiente.

        Raises:
            PedidoVacio, CantidadInvalida, ProductoNoDisponible: si la selección no
                cumple RN-NEG-01 o RN-NEG-02; el pedido no se confirma (PN-01, paso 7).
        """
        return cls(
            codigo_retiro=codigo_retiro,
            cliente_id=cliente_id,
            detalles=construir_detalles(seleccion),
            estado=EstadoPedido.PENDIENTE,
            fecha_registro=momento or ahora(),
        )

    @property
    def total(self) -> Decimal:
        """Importe total, calculado desde los detalles (RN-NEG-03)."""
        return calcular_total(self.detalles)

    @property
    def cantidad_articulos(self) -> int:
        """Suma de las unidades de todos los productos."""
        return sum(detalle.cantidad for detalle in self.detalles)

    def fecha_de(self, estado: EstadoPedido) -> datetime | None:
        """Devuelve el momento en que el pedido llegó a un estado, si ya llegó."""
        return {
            EstadoPedido.PENDIENTE: self.fecha_registro,
            EstadoPedido.EN_PREPARACION: self.fecha_preparacion,
            EstadoPedido.LISTO_PARA_RETIRAR: self.fecha_listo,
            EstadoPedido.ENTREGADO: self.fecha_entrega,
        }[estado]

    def avanzar(self, momento: datetime | None = None) -> None:
        """Pasa el pedido al estado siguiente: Pendiente → En preparación → Listo.

        Args:
            momento: fecha del cambio; por defecto, la hora actual.

        Raises:
            TransicionNoPermitida: si el pedido está Listo para retirar (la entrega
                exige el código, RN-NEG-07) o ya fue entregado.
        """
        if self.estado is EstadoPedido.LISTO_PARA_RETIRAR:
            raise exc.TransicionNoPermitida(
                "Para entregar el pedido se debe verificar el código de retiro."
            )
        siguiente = self.estado.siguiente
        if siguiente is None:
            raise exc.TransicionNoPermitida("El pedido ya fue entregado y no puede cambiar.")
        self._pasar_a(siguiente, momento or ahora())

    def entregar(self, codigo_presentado: str, momento: datetime | None = None) -> None:
        """Registra la entrega si el pedido está listo y el código coincide (RN-NEG-07).

        Args:
            codigo_presentado: código que muestra el cliente; se normaliza antes de
                compararlo.
            momento: fecha de la entrega; por defecto, la hora actual.

        Raises:
            TransicionNoPermitida: si el pedido no está Listo para retirar.
            CodigoRetiroIncorrecto: si el código no coincide.
        """
        if self.estado is not EstadoPedido.LISTO_PARA_RETIRAR:
            raise exc.TransicionNoPermitida(
                f"El pedido está {self.estado.etiqueta}; solo se entrega cuando está "
                "Listo para retirar."
            )
        if normalizar_codigo_retiro(codigo_presentado) != self.codigo_retiro:
            raise exc.CodigoRetiroIncorrecto()
        self._pasar_a(EstadoPedido.ENTREGADO, momento or ahora())

    def _pasar_a(self, estado: EstadoPedido, momento: datetime) -> None:
        self.estado = estado
        if estado is EstadoPedido.EN_PREPARACION:
            self.fecha_preparacion = momento
        elif estado is EstadoPedido.LISTO_PARA_RETIRAR:
            self.fecha_listo = momento
        elif estado is EstadoPedido.ENTREGADO:
            self.fecha_entrega = momento
