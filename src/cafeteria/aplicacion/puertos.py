"""Interfaces (puertos) que la capa de aplicación necesita de la persistencia.

Los servicios dependen de estos protocolos y no de SQLite; la capa de infraestructura
los implementa (inversión de dependencias). Un cambio de motor de base de datos afecta
solo a la infraestructura.
"""

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from cafeteria.dominio.modelos import Categoria, Cliente, EstadoPedido, Pedido, Producto


class RepositorioProductos(Protocol):
    """Almacén de los productos del menú."""

    def listar(self, *, solo_disponibles: bool = False) -> list[Producto]:
        """Devuelve los productos ordenados por categoría y nombre."""
        ...

    def obtener(self, codigo: str) -> Producto | None:
        """Busca un producto por su código."""
        ...

    def siguiente_codigo(self, categoria: Categoria) -> str:
        """Calcula el código que corresponde a un producto nuevo de la categoría."""
        ...

    def agregar(self, producto: Producto) -> Producto:
        """Guarda un producto nuevo y devuelve el producto con su id."""
        ...

    def actualizar(self, producto: Producto) -> None:
        """Guarda los cambios de un producto existente."""
        ...


class RepositorioClientes(Protocol):
    """Almacén de los clientes registrados."""

    def agregar(self, cliente: Cliente) -> Cliente:
        """Guarda un cliente nuevo y devuelve el cliente con su id y su código.

        Raises:
            ClienteDuplicado: si la cédula o el correo ya están registrados.
        """
        ...

    def obtener(self, cliente_id: int) -> Cliente | None:
        """Busca un cliente por su id."""
        ...

    def buscar_por_correo(self, correo: str) -> Cliente | None:
        """Busca un cliente por su correo institucional."""
        ...

    def buscar_por_cedula(self, cedula: str) -> Cliente | None:
        """Busca un cliente por su cédula."""
        ...


class RepositorioPedidos(Protocol):
    """Almacén de los pedidos confirmados y sus detalles."""

    def agregar(self, pedido: Pedido) -> Pedido:
        """Guarda un pedido con sus detalles en una sola transacción.

        Raises:
            CodigoRetiroDuplicado: si el código de retiro ya existe.
        """
        ...

    def obtener(self, pedido_id: int) -> Pedido | None:
        """Busca un pedido por su id."""
        ...

    def obtener_por_codigo(self, codigo_retiro: str) -> Pedido | None:
        """Busca un pedido por su código de retiro."""
        ...

    def listar_por_cliente(self, cliente_id: int) -> list[Pedido]:
        """Devuelve los pedidos de un cliente, del más reciente al más antiguo."""
        ...

    def listar_por_estados(self, estados: Iterable[EstadoPedido]) -> list[Pedido]:
        """Devuelve los pedidos en esos estados, del más antiguo al más reciente."""
        ...

    def actualizar_estado(self, pedido: Pedido, estado_anterior: EstadoPedido) -> None:
        """Guarda el nuevo estado solo si el pedido seguía en ``estado_anterior``.

        Raises:
            TransicionNoPermitida: si otro usuario cambió el estado antes.
        """
        ...

    def contar_entregados_desde(self, momento: datetime) -> int:
        """Cuenta los pedidos entregados desde un momento dado."""
        ...
