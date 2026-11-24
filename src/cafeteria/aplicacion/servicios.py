"""Servicios de aplicación: coordinan los casos de uso entre el dominio y la persistencia.

Las reglas de negocio viven en ``cafeteria.dominio``; los servicios obtienen los datos,
invocan al dominio y guardan el resultado.
"""

import hmac
from collections.abc import Callable, Mapping
from datetime import datetime
from decimal import Decimal

from cafeteria.aplicacion.puertos import (
    RepositorioClientes,
    RepositorioPedidos,
    RepositorioProductos,
)
from cafeteria.dominio import excepciones as exc
from cafeteria.dominio.codigo_retiro import generar_codigo_retiro
from cafeteria.dominio.modelos import (
    Categoria,
    Cliente,
    DetallePedido,
    EstadoPedido,
    Pedido,
    Producto,
    ahora,
    calcular_total,
    construir_detalles,
)

ESTADOS_EN_CURSO = (
    EstadoPedido.PENDIENTE,
    EstadoPedido.EN_PREPARACION,
    EstadoPedido.LISTO_PARA_RETIRAR,
)


def _categoria(valor: str | Categoria) -> Categoria:
    try:
        return Categoria(valor)
    except ValueError:
        raise exc.DatoInvalido("Elige una categoría: Alimentos o Bebidas.") from None


class ServicioMenu:
    """Consulta del menú (HU-01) y mantenimiento de productos (HU-07).

    Args:
        productos: repositorio de productos.
    """

    def __init__(self, productos: RepositorioProductos) -> None:
        self._productos = productos

    def listar(self, *, solo_disponibles: bool = False) -> list[Producto]:
        """Devuelve el menú ordenado por categoría y nombre.

        Args:
            solo_disponibles: si es True, excluye los productos no disponibles.
        """
        return self._productos.listar(solo_disponibles=solo_disponibles)

    def obtener(self, codigo: str) -> Producto:
        """Devuelve un producto por su código.

        Raises:
            ProductoNoEncontrado: si no existe.
        """
        producto = self._productos.obtener(codigo)
        if producto is None:
            raise exc.ProductoNoEncontrado()
        return producto

    def registrar(
        self, *, nombre: str, categoria: str | Categoria, precio: Decimal | str, disponible: bool
    ) -> Producto:
        """Agrega un producto al menú con un código asignado por el sistema (supuesto A5).

        Returns:
            Producto: el producto guardado, por ejemplo con código ``BEB-004``.

        Raises:
            DatoInvalido: si el nombre, la categoría o el precio no son válidos.
        """
        categoria_valida = _categoria(categoria)
        producto = Producto(
            codigo=self._productos.siguiente_codigo(categoria_valida),
            nombre=nombre,
            categoria=categoria_valida,
            precio=precio,
            disponible=disponible,
        )
        return self._productos.agregar(producto)

    def actualizar(
        self,
        codigo: str,
        *,
        nombre: str,
        categoria: str | Categoria,
        precio: Decimal | str,
        disponible: bool,
    ) -> Producto:
        """Cambia los datos de un producto; no afecta los pedidos ya confirmados (RN-NEG-04).

        Raises:
            ProductoNoEncontrado: si no existe.
            DatoInvalido: si algún dato no es válido.
        """
        producto = self.obtener(codigo)
        producto.actualizar(
            nombre=nombre, categoria=_categoria(categoria), precio=precio, disponible=disponible
        )
        self._productos.actualizar(producto)
        return producto

    def cambiar_disponibilidad(self, codigo: str, disponible: bool) -> Producto:
        """Marca un producto como disponible o no disponible (RN-NEG-02).

        Raises:
            ProductoNoEncontrado: si no existe.
        """
        producto = self.obtener(codigo)
        producto.disponible = disponible
        self._productos.actualizar(producto)
        return producto


class ServicioClientes:
    """Registro e identificación de clientes (HU-06, supuesto A1).

    Args:
        clientes: repositorio de clientes.
        dominio_correo: dominio del correo institucional, por ejemplo ``epn.edu.ec``.
    """

    def __init__(self, clientes: RepositorioClientes, dominio_correo: str) -> None:
        self._clientes = clientes
        self.dominio_correo = dominio_correo

    def registrar(
        self, *, nombre: str, apellido: str, cedula: str, celular: str, correo: str
    ) -> Cliente:
        """Registra un cliente nuevo y le asigna un código ``CLI-0001``.

        Raises:
            DatoInvalido: si algún dato no es válido.
            ClienteDuplicado: si la cédula o el correo ya están registrados.
        """
        cliente = Cliente.nuevo(
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            celular=celular,
            correo=correo,
            dominio=self.dominio_correo,
        )
        if self._clientes.buscar_por_cedula(cliente.cedula):
            raise exc.ClienteDuplicado(
                "Ya existe un cliente con esa cédula. Ingresa con tu correo y tu cédula."
            )
        if self._clientes.buscar_por_correo(cliente.correo):
            raise exc.ClienteDuplicado(
                "Ya existe un cliente con ese correo. Ingresa con tu correo y tu cédula."
            )
        return self._clientes.agregar(cliente)

    def identificar(self, *, correo: str, cedula: str) -> Cliente:
        """Identifica a un cliente con su correo y su cédula (sin contraseña, supuesto A1).

        Raises:
            CredencialesInvalidas: si no hay un cliente con ese correo y esa cédula.
        """
        cliente = self._clientes.buscar_por_correo(correo.strip().lower())
        if cliente is None or not hmac.compare_digest(
            cliente.cedula.encode(), cedula.strip().encode()
        ):
            raise exc.CredencialesInvalidas(
                "No encontramos un cliente con ese correo y esa cédula."
            )
        return cliente

    def obtener(self, cliente_id: int) -> Cliente | None:
        """Devuelve un cliente por su id, o None si no existe."""
        return self._clientes.obtener(cliente_id)


class ServicioPedidos:
    """Registro (PN-01) y atención (PN-02) de pedidos.

    Args:
        pedidos: repositorio de pedidos.
        productos: repositorio de productos.
        generar_codigo: función que genera códigos de retiro; se reemplaza en pruebas.
        reloj: función que devuelve la hora actual; se reemplaza en pruebas.
    """

    INTENTOS_CODIGO = 5

    def __init__(
        self,
        pedidos: RepositorioPedidos,
        productos: RepositorioProductos,
        *,
        generar_codigo: Callable[[], str] = generar_codigo_retiro,
        reloj: Callable[[], datetime] = ahora,
    ) -> None:
        self._pedidos = pedidos
        self._productos = productos
        self._generar_codigo = generar_codigo
        self._reloj = reloj

    def _seleccion(self, cantidades: Mapping[str, int]) -> list[tuple[Producto, int]]:
        seleccion = []
        for codigo, cantidad in cantidades.items():
            producto = self._productos.obtener(codigo)
            if producto is None:
                raise exc.ProductoNoEncontrado()
            seleccion.append((producto, cantidad))
        return seleccion

    def revisar(self, cantidades: Mapping[str, int]) -> tuple[tuple[DetallePedido, ...], Decimal]:
        """Valida la selección y calcula el total sin guardar nada (HU-03, RU-03).

        Args:
            cantidades: código de producto → unidades.

        Returns:
            tuple: los detalles con el precio vigente y el importe total.

        Raises:
            PedidoVacio, CantidadInvalida, ProductoNoDisponible, ProductoNoEncontrado:
                si la selección no cumple las reglas.
        """
        detalles = construir_detalles(self._seleccion(cantidades))
        return detalles, calcular_total(detalles)

    def confirmar(self, cliente_id: int, cantidades: Mapping[str, int]) -> Pedido:
        """Confirma un pedido en estado Pendiente con un código de retiro único (HU-04).

        Si el código generado ya existe, genera otro, hasta ``INTENTOS_CODIGO`` veces
        (RN-NEG-05).

        Args:
            cliente_id: cliente que confirma.
            cantidades: código de producto → unidades.

        Returns:
            Pedido: el pedido guardado.

        Raises:
            PedidoVacio, CantidadInvalida, ProductoNoDisponible, ProductoNoEncontrado:
                si la selección no cumple las reglas; el pedido no se confirma.
        """
        seleccion = self._seleccion(cantidades)
        for _ in range(self.INTENTOS_CODIGO):
            pedido = Pedido.confirmar(
                cliente_id=cliente_id,
                seleccion=seleccion,
                codigo_retiro=self._generar_codigo(),
                momento=self._reloj(),
            )
            try:
                return self._pedidos.agregar(pedido)
            except exc.CodigoRetiroDuplicado:
                continue
        raise exc.ErrorDeNegocio("No se pudo generar un código de retiro. Intenta de nuevo.")

    def obtener(self, pedido_id: int) -> Pedido:
        """Devuelve un pedido por su id.

        Raises:
            PedidoNoEncontrado: si no existe.
        """
        pedido = self._pedidos.obtener(pedido_id)
        if pedido is None:
            raise exc.PedidoNoEncontrado()
        return pedido

    def obtener_por_codigo(self, codigo_retiro: str) -> Pedido:
        """Devuelve un pedido por su código de retiro.

        Raises:
            PedidoNoEncontrado: si no existe.
        """
        pedido = self._pedidos.obtener_por_codigo(codigo_retiro)
        if pedido is None:
            raise exc.PedidoNoEncontrado()
        return pedido

    def pedidos_de_cliente(self, cliente_id: int) -> list[Pedido]:
        """Devuelve los pedidos de un cliente, del más reciente al más antiguo (HU-05)."""
        return self._pedidos.listar_por_cliente(cliente_id)

    def tablero(self) -> dict[EstadoPedido, list[Pedido]]:
        """Agrupa los pedidos en curso por estado, del más antiguo al más reciente (HU-08)."""
        columnas: dict[EstadoPedido, list[Pedido]] = {estado: [] for estado in ESTADOS_EN_CURSO}
        for pedido in self._pedidos.listar_por_estados(ESTADOS_EN_CURSO):
            columnas[pedido.estado].append(pedido)
        return columnas

    def entregados_hoy(self) -> int:
        """Cuenta los pedidos entregados desde la medianoche de hoy."""
        inicio_del_dia = self._reloj().replace(hour=0, minute=0, second=0, microsecond=0)
        return self._pedidos.contar_entregados_desde(inicio_del_dia)

    def avanzar(self, pedido_id: int) -> Pedido:
        """Registra el avance: Pendiente → En preparación → Listo para retirar (HU-09).

        Raises:
            PedidoNoEncontrado: si no existe.
            TransicionNoPermitida: si el cambio viola RN-NEG-06 o RN-NEG-07.
        """
        pedido = self.obtener(pedido_id)
        estado_anterior = pedido.estado
        pedido.avanzar(self._reloj())
        self._pedidos.actualizar_estado(pedido, estado_anterior)
        return pedido

    def entregar(self, pedido_id: int, codigo_presentado: str) -> Pedido:
        """Registra la entrega si el pedido está listo y el código coincide (HU-10).

        Raises:
            PedidoNoEncontrado: si no existe.
            TransicionNoPermitida: si el pedido no está Listo para retirar.
            CodigoRetiroIncorrecto: si el código no coincide (RN-NEG-07).
        """
        pedido = self.obtener(pedido_id)
        estado_anterior = pedido.estado
        pedido.entregar(codigo_presentado, self._reloj())
        self._pedidos.actualizar_estado(pedido, estado_anterior)
        return pedido


class ServicioAccesoPersonal:
    """Verifica las credenciales de la cuenta del personal (HU-11, supuesto A4).

    Args:
        usuario: usuario configurado por variable de entorno.
        clave: clave configurada por variable de entorno.
    """

    def __init__(self, usuario: str, clave: str) -> None:
        self._usuario = usuario.encode()
        self._clave = clave.encode()

    def verificar(self, usuario: str, clave: str) -> None:
        """Comprueba el usuario y la clave en tiempo constante.

        Raises:
            CredencialesInvalidas: si no coinciden.
        """
        usuario_ok = hmac.compare_digest(usuario.strip().encode(), self._usuario)
        clave_ok = hmac.compare_digest(clave.encode(), self._clave)
        if not (usuario_ok and clave_ok):
            raise exc.CredencialesInvalidas("Usuario o clave incorrectos.")
