"""Conexión y esquema de la base de datos SQLite.

La base de datos es un archivo; en Docker se guarda en un volumen nombrado para que
los datos persistan entre ejecuciones (especificación §8, RNF-01).
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL CHECK (categoria IN ('ALIMENTO', 'BEBIDA')),
    precio_centavos INTEGER NOT NULL CHECK (precio_centavos > 0),
    disponible INTEGER NOT NULL DEFAULT 1 CHECK (disponible IN (0, 1))
);

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    cedula TEXT NOT NULL UNIQUE,
    celular TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_retiro TEXT NOT NULL UNIQUE,
    cliente_id INTEGER NOT NULL REFERENCES clientes (id),
    estado TEXT NOT NULL CHECK (
        estado IN ('PENDIENTE', 'EN_PREPARACION', 'LISTO_PARA_RETIRAR', 'ENTREGADO')
    ),
    fecha_registro TEXT NOT NULL,
    fecha_preparacion TEXT,
    fecha_listo TEXT,
    fecha_entrega TEXT
);

CREATE TABLE IF NOT EXISTS detalles_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
    producto_codigo TEXT NOT NULL REFERENCES productos (codigo),
    producto_nombre TEXT NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario_centavos INTEGER NOT NULL CHECK (precio_unitario_centavos > 0)
);

CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos (estado);
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos (cliente_id);
CREATE INDEX IF NOT EXISTS idx_detalles_pedido ON detalles_pedido (pedido_id);
"""


class BaseDatos:
    """Abre conexiones a la base de datos SQLite y crea su esquema.

    Cada operación usa su propia conexión como unidad de trabajo: se confirma si termina
    sin errores y se revierte si ocurre una excepción.

    Args:
        ruta: ruta del archivo de la base de datos.
    """

    def __init__(self, ruta: str | Path) -> None:
        self.ruta = Path(ruta)

    def crear_esquema(self) -> None:
        """Crea la carpeta, las tablas y los índices si no existen."""
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.conexion() as con:
            con.execute("PRAGMA journal_mode = WAL")
            con.executescript(ESQUEMA)

    @contextmanager
    def conexion(self) -> Iterator[sqlite3.Connection]:
        """Abre una conexión con claves foráneas activas y filas accesibles por nombre.

        Yields:
            sqlite3.Connection: la conexión abierta.
        """
        con = sqlite3.connect(self.ruta, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()
