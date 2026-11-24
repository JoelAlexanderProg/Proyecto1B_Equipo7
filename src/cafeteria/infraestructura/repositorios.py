"""Implementación de los repositorios con SQLite.

Los montos se guardan como centavos enteros y las fechas en formato ISO 8601 con la
zona horaria de Ecuador, para evitar errores de redondeo y de comparación.
"""

import sqlite3
import uuid
from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime
from decimal import Decimal

from cafeteria.dominio import excepciones as exc
from cafeteria.dominio.modelos import (
    Categoria,
    Cliente,
    DetallePedido,
    EstadoPedido,
    Pedido,
    Producto,
)
from cafeteria.infraestructura.basedatos import BaseDatos

_CENTAVO = Decimal("0.01")


def _a_centavos(valor: Decimal) -> int:
    return int(valor * 100)


def _de_centavos(centavos: int) -> Decimal:
    return (Decimal(centavos) / 100).quantize(_CENTAVO)


def _a_texto(fecha: datetime | None) -> str | None:
    return fecha.isoformat() if fecha else None


def _a_fecha(texto: str | None) -> datetime | None:
    return datetime.fromisoformat(texto) if texto else None


class RepositorioProductosSQLite:
    """Repositorio de productos sobre la tabla ``productos``.

    Args:
        bd: base de datos.
    """

    def __init__(self, bd: BaseDatos) -> None:
        self._bd = bd

    @staticmethod
    def _producto(fila: sqlite3.Row) -> Producto:
        return Producto(
            codigo=fila["codigo"],
            nombre=fila["nombre"],
            categoria=Categoria(fila["categoria"]),
            precio=_de_centavos(fila["precio_centavos"]),
            disponible=bool(fila["disponible"]),
            id=fila["id"],
        )

    def listar(self, *, solo_disponibles: bool = False) -> list[Producto]:
        """Devuelve los productos ordenados por categoría y nombre."""
        consulta = "SELECT * FROM productos"
        if solo_disponibles:
            consulta += " WHERE disponible = 1"
        with self._bd.conexion() as con:
            filas = con.execute(consulta + " ORDER BY categoria, nombre").fetchall()
        return [self._producto(fila) for fila in filas]

    def obtener(self, codigo: str) -> Producto | None:
        """Busca un producto por su código."""
        with self._bd.conexion() as con:
            fila = con.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,)).fetchone()
        return self._producto(fila) if fila else None

    def siguiente_codigo(self, categoria: Categoria) -> str:
        """Devuelve el siguiente código de la categoría, por ejemplo ``ALI-007``."""
        with self._bd.conexion() as con:
            fila = con.execute(
                "SELECT codigo FROM productos WHERE codigo LIKE ? ORDER BY codigo DESC LIMIT 1",
                (f"{categoria.prefijo}-%",),
            ).fetchone()
        ultimo = int(fila["codigo"].split("-")[1]) if fila else 0
        return f"{categoria.prefijo}-{ultimo + 1:03d}"

    def agregar(self, producto: Producto) -> Producto:
        """Guarda un producto nuevo y devuelve el producto con su id."""
        with self._bd.conexion() as con:
            cursor = con.execute(
                "INSERT INTO productos (codigo, nombre, categoria, precio_centavos, disponible)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    producto.codigo,
                    producto.nombre,
                    producto.categoria.value,
                    _a_centavos(producto.precio),
                    int(producto.disponible),
                ),
            )
        producto.id = cursor.lastrowid
        return producto

    def actualizar(self, producto: Producto) -> None:
        """Guarda los cambios de un producto existente."""
        with self._bd.conexion() as con:
            con.execute(
                "UPDATE productos SET nombre = ?, categoria = ?, precio_centavos = ?,"
                " disponible = ? WHERE codigo = ?",
                (
                    producto.nombre,
                    producto.categoria.value,
                    _a_centavos(producto.precio),
                    int(producto.disponible),
                    producto.codigo,
                ),
            )


class RepositorioClientesSQLite:
    """Repositorio de clientes sobre la tabla ``clientes``.

    Args:
        bd: base de datos.
    """

    def __init__(self, bd: BaseDatos) -> None:
        self._bd = bd

    @staticmethod
    def _cliente(fila: sqlite3.Row) -> Cliente:
        return Cliente(
            codigo=fila["codigo"],
            nombre=fila["nombre"],
            apellido=fila["apellido"],
            cedula=fila["cedula"],
            celular=fila["celular"],
            correo=fila["correo"],
            id=fila["id"],
        )

    def _buscar(self, campo: str, valor: object) -> Cliente | None:
        with self._bd.conexion() as con:
            fila = con.execute(f"SELECT * FROM clientes WHERE {campo} = ?", (valor,)).fetchone()
        return self._cliente(fila) if fila else None

    def agregar(self, cliente: Cliente) -> Cliente:
        """Guarda un cliente y le asigna el código ``CLI-0001`` según su id.

        Raises:
            ClienteDuplicado: si la cédula o el correo ya están registrados.
        """
        try:
            with self._bd.conexion() as con:
                cursor = con.execute(
                    "INSERT INTO clientes (codigo, nombre, apellido, cedula, celular, correo)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        f"TMP-{uuid.uuid4().hex}",
                        cliente.nombre,
                        cliente.apellido,
                        cliente.cedula,
                        cliente.celular,
                        cliente.correo,
                    ),
                )
                cliente_id = cursor.lastrowid
                codigo = f"CLI-{cliente_id:04d}"
                con.execute("UPDATE clientes SET codigo = ? WHERE id = ?", (codigo, cliente_id))
        except sqlite3.IntegrityError:
            mensaje = "Ya existe un cliente con esa cédula o ese correo."
            raise exc.ClienteDuplicado(mensaje) from None
        return replace(cliente, id=cliente_id, codigo=codigo)

    def obtener(self, cliente_id: int) -> Cliente | None:
        """Busca un cliente por su id."""
        return self._buscar("id", cliente_id)

    def buscar_por_correo(self, correo: str) -> Cliente | None:
        """Busca un cliente por su correo institucional."""
        return self._buscar("correo", correo)

    def buscar_por_cedula(self, cedula: str) -> Cliente | None:
        """Busca un cliente por su cédula."""
        return self._buscar("cedula", cedula)


class RepositorioPedidosSQLite:
    """Repositorio de pedidos sobre las tablas ``pedidos`` y ``detalles_pedido``.

    Args:
        bd: base de datos.
    """

    def __init__(self, bd: BaseDatos) -> None:
        self._bd = bd

    @staticmethod
    def _construir(con: sqlite3.Connection, filas: list[sqlite3.Row]) -> list[Pedido]:
        """Arma los pedidos cargando los detalles de todos en una sola consulta."""
        if not filas:
            return []
        ids = [fila["id"] for fila in filas]
        marcadores = ", ".join("?" for _ in ids)
        detalles: dict[int, list[DetallePedido]] = {pedido_id: [] for pedido_id in ids}
        for fila in con.execute(
            f"SELECT * FROM detalles_pedido WHERE pedido_id IN ({marcadores}) ORDER BY id", ids
        ):
            detalles[fila["pedido_id"]].append(
                DetallePedido(
                    producto_codigo=fila["producto_codigo"],
                    producto_nombre=fila["producto_nombre"],
                    cantidad=fila["cantidad"],
                    precio_unitario=_de_centavos(fila["precio_unitario_centavos"]),
                )
            )
        return [
            Pedido(
                codigo_retiro=fila["codigo_retiro"],
                cliente_id=fila["cliente_id"],
                detalles=tuple(detalles[fila["id"]]),
                estado=EstadoPedido(fila["estado"]),
                fecha_registro=_a_fecha(fila["fecha_registro"]),
                fecha_preparacion=_a_fecha(fila["fecha_preparacion"]),
                fecha_listo=_a_fecha(fila["fecha_listo"]),
                fecha_entrega=_a_fecha(fila["fecha_entrega"]),
                id=fila["id"],
            )
            for fila in filas
        ]

    def _consultar(self, condicion: str, parametros: Iterable[object]) -> list[Pedido]:
        with self._bd.conexion() as con:
            filas = con.execute(f"SELECT * FROM pedidos {condicion}", tuple(parametros)).fetchall()
            return self._construir(con, filas)

    def agregar(self, pedido: Pedido) -> Pedido:
        """Guarda el pedido y sus detalles en una sola transacción.

        Raises:
            CodigoRetiroDuplicado: si el código de retiro ya existe (RN-NEG-05).
        """
        try:
            with self._bd.conexion() as con:
                cursor = con.execute(
                    "INSERT INTO pedidos (codigo_retiro, cliente_id, estado, fecha_registro)"
                    " VALUES (?, ?, ?, ?)",
                    (
                        pedido.codigo_retiro,
                        pedido.cliente_id,
                        pedido.estado.value,
                        _a_texto(pedido.fecha_registro),
                    ),
                )
                pedido_id = cursor.lastrowid
                con.executemany(
                    "INSERT INTO detalles_pedido (pedido_id, producto_codigo, producto_nombre,"
                    " cantidad, precio_unitario_centavos) VALUES (?, ?, ?, ?, ?)",
                    [
                        (
                            pedido_id,
                            detalle.producto_codigo,
                            detalle.producto_nombre,
                            detalle.cantidad,
                            _a_centavos(detalle.precio_unitario),
                        )
                        for detalle in pedido.detalles
                    ],
                )
        except sqlite3.IntegrityError as error:
            if "codigo_retiro" in str(error):
                raise exc.CodigoRetiroDuplicado() from error
            raise
        pedido.id = pedido_id
        return pedido

    def obtener(self, pedido_id: int) -> Pedido | None:
        """Busca un pedido por su id."""
        pedidos = self._consultar("WHERE id = ?", (pedido_id,))
        return pedidos[0] if pedidos else None

    def obtener_por_codigo(self, codigo_retiro: str) -> Pedido | None:
        """Busca un pedido por su código de retiro."""
        pedidos = self._consultar("WHERE codigo_retiro = ?", (codigo_retiro,))
        return pedidos[0] if pedidos else None

    def listar_por_cliente(self, cliente_id: int) -> list[Pedido]:
        """Devuelve los pedidos del cliente, del más reciente al más antiguo."""
        return self._consultar(
            "WHERE cliente_id = ? ORDER BY fecha_registro DESC, id DESC", (cliente_id,)
        )

    def listar_por_estados(self, estados: Iterable[EstadoPedido]) -> list[Pedido]:
        """Devuelve los pedidos en esos estados, del más antiguo al más reciente."""
        valores = [estado.value for estado in estados]
        marcadores = ", ".join("?" for _ in valores)
        return self._consultar(
            f"WHERE estado IN ({marcadores}) ORDER BY fecha_registro, id", valores
        )

    def actualizar_estado(self, pedido: Pedido, estado_anterior: EstadoPedido) -> None:
        """Guarda el nuevo estado solo si el pedido seguía en ``estado_anterior``.

        Es un control optimista: evita que dos personas del personal registren a la vez
        cambios incompatibles sobre el mismo pedido.

        Raises:
            TransicionNoPermitida: si el estado cambió entre la lectura y la escritura.
        """
        with self._bd.conexion() as con:
            cursor = con.execute(
                "UPDATE pedidos SET estado = ?, fecha_preparacion = ?, fecha_listo = ?,"
                " fecha_entrega = ? WHERE id = ? AND estado = ?",
                (
                    pedido.estado.value,
                    _a_texto(pedido.fecha_preparacion),
                    _a_texto(pedido.fecha_listo),
                    _a_texto(pedido.fecha_entrega),
                    pedido.id,
                    estado_anterior.value,
                ),
            )
        if cursor.rowcount == 0:
            raise exc.TransicionNoPermitida(
                "El pedido cambió de estado mientras lo atendías. Actualiza el tablero."
            )

    def contar_entregados_desde(self, momento: datetime) -> int:
        """Cuenta los pedidos entregados desde un momento dado."""
        with self._bd.conexion() as con:
            fila = con.execute(
                "SELECT COUNT(*) AS total FROM pedidos WHERE estado = ? AND fecha_entrega >= ?",
                (EstadoPedido.ENTREGADO.value, momento.isoformat()),
            ).fetchone()
        return fila["total"]
