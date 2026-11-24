"""Páginas del cliente: menú, pedido, seguimiento, registro e ingreso (PN-01)."""

from decimal import Decimal, InvalidOperation
from itertools import groupby
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from cafeteria.dominio import excepciones as exc
from cafeteria.dominio.modelos import EstadoPedido, Producto
from cafeteria.presentacion.dependencias import cliente_actual, servicios
from cafeteria.presentacion.plantillas import avisar, mostrar, redirigir

router = APIRouter(include_in_schema=False)

PREFIJO_CANTIDAD = "cant-"
RUTA_INGRESO = "/ingresar"
Campo = Annotated[str, Form()]


def agrupar_por_categoria(productos: list[Producto]) -> list[tuple]:
    """Agrupa los productos ya ordenados por categoría: [(categoría, [productos])]."""
    return [
        (categoria, list(grupo)) for categoria, grupo in groupby(productos, lambda p: p.categoria)
    ]


def leer_cantidades(formulario) -> dict[str, int]:
    """Extrae del formulario del menú las cantidades mayores que cero.

    Un campo vacío o en 0 significa que el producto no se eligió; cualquier otro valor
    pasa al dominio, que aplica RN-NEG-01.

    Args:
        formulario: datos enviados; los campos se llaman ``cant-<código>``.

    Returns:
        dict[str, int]: código de producto → unidades.

    Raises:
        CantidadInvalida: si una cantidad no es un número entero.
    """
    cantidades = {}
    for clave, valor in formulario.items():
        if not clave.startswith(PREFIJO_CANTIDAD):
            continue
        texto = str(valor).strip()
        if texto in {"", "0"}:
            continue
        try:
            cantidades[clave.removeprefix(PREFIJO_CANTIDAD)] = int(texto)
        except ValueError:
            raise exc.CantidadInvalida("Las cantidades deben ser números enteros.") from None
    return cantidades


def _menu(request: Request, error: str | None = None, status_code: int = 200) -> HTMLResponse:
    contexto = {
        "cliente": cliente_actual(request),
        "grupos": agrupar_por_categoria(servicios(request).menu.listar()),
        "borrador": request.session.get("borrador", {}),
        "error": error,
    }
    return mostrar(request, "cliente/menu.html", contexto, status_code)


def _revision(request: Request, cliente, cantidades, error: str | None = None) -> HTMLResponse:
    detalles, total = servicios(request).pedidos.revisar(cantidades)
    contexto = {"cliente": cliente, "detalles": detalles, "total": total, "error": error}
    return mostrar(request, "cliente/revisar.html", contexto)


@router.get("/", response_class=HTMLResponse)
def ver_menu(request: Request) -> HTMLResponse:
    """Menú con los productos, sus precios y su disponibilidad (HU-01)."""
    return _menu(request)


@router.post("/pedido/revisar")
async def revisar_pedido(request: Request) -> Response:
    """Valida la selección y muestra el total antes de confirmar (HU-02, HU-03)."""
    cliente = cliente_actual(request)
    if cliente is None:
        return redirigir(RUTA_INGRESO)
    try:
        cantidades = leer_cantidades(await request.form())
        request.session["borrador"] = cantidades
        return _revision(request, cliente, cantidades)
    except exc.ErrorDeNegocio as error:
        return _menu(request, error.mensaje, status_code=422)


@router.post("/pedido/confirmar")
def confirmar_pedido(request: Request, total_revisado: Campo = "") -> Response:
    """Confirma el pedido y muestra el código de retiro (HU-04, PN-01).

    Si un precio cambió después de la revisión, vuelve a mostrar el total en lugar de
    confirmar, porque el cliente debe conocer el importe antes de confirmar (RU-03).
    """
    cliente = cliente_actual(request)
    if cliente is None:
        return redirigir(RUTA_INGRESO)
    cantidades = request.session.get("borrador") or {}
    pedidos = servicios(request).pedidos
    try:
        _, total_actual = pedidos.revisar(cantidades)
        if _monto(total_revisado) != total_actual:
            aviso = "Un precio cambió mientras revisabas. Revisa el nuevo total y confirma."
            return _revision(request, cliente, cantidades, aviso)
        pedido = pedidos.confirmar(cliente.id, cantidades)
    except exc.ErrorDeNegocio as error:
        return _menu(request, error.mensaje, status_code=422)
    request.session.pop("borrador", None)
    return redirigir(f"/pedidos/{pedido.codigo_retiro}")


def _monto(texto: str) -> Decimal | None:
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


@router.get("/pedidos/{codigo}", response_class=HTMLResponse)
def ver_pedido(request: Request, codigo: str) -> Response:
    """Ticket con el código de retiro y el seguimiento del estado (HU-05)."""
    cliente = cliente_actual(request)
    if cliente is None:
        return redirigir(RUTA_INGRESO)
    try:
        pedido = servicios(request).pedidos.obtener_por_codigo(codigo.upper())
    except exc.PedidoNoEncontrado:
        raise HTTPException(404) from None
    if pedido.cliente_id != cliente.id:
        raise HTTPException(404)
    contexto = {"cliente": cliente, "pedido": pedido, "estados": list(EstadoPedido)}
    return mostrar(request, "cliente/pedido.html", contexto)


@router.get("/mis-pedidos", response_class=HTMLResponse)
def mis_pedidos(request: Request) -> Response:
    """Lista de los pedidos del cliente con su estado (HU-05)."""
    cliente = cliente_actual(request)
    if cliente is None:
        return redirigir(RUTA_INGRESO)
    pedidos = servicios(request).pedidos.pedidos_de_cliente(cliente.id)
    return mostrar(request, "cliente/mis_pedidos.html", {"cliente": cliente, "pedidos": pedidos})


@router.get(RUTA_INGRESO, response_class=HTMLResponse)
def formulario_ingreso(request: Request) -> HTMLResponse:
    """Formulario de ingreso con correo y cédula (supuesto A1)."""
    return mostrar(request, "cliente/ingresar.html", {"datos": {}})


@router.post(RUTA_INGRESO)
def ingresar(request: Request, correo: Campo = "", cedula: Campo = "") -> Response:
    """Identifica al cliente y guarda su id en la sesión."""
    try:
        cliente = servicios(request).clientes.identificar(correo=correo, cedula=cedula)
    except exc.ErrorDeNegocio as error:
        contexto = {"datos": {"correo": correo}, "error": error.mensaje}
        return mostrar(request, "cliente/ingresar.html", contexto, status_code=422)
    request.session["cliente_id"] = cliente.id
    return redirigir("/")


@router.get("/registro", response_class=HTMLResponse)
def formulario_registro(request: Request) -> HTMLResponse:
    """Formulario de registro de cliente (HU-06)."""
    dominio = servicios(request).clientes.dominio_correo
    return mostrar(request, "cliente/registro.html", {"datos": {}, "dominio": dominio})


@router.post("/registro")
def registrar(
    request: Request,
    nombre: Campo = "",
    apellido: Campo = "",
    cedula: Campo = "",
    celular: Campo = "",
    correo: Campo = "",
) -> Response:
    """Registra al cliente, inicia su sesión y le muestra su código de cliente."""
    datos = {
        "nombre": nombre,
        "apellido": apellido,
        "cedula": cedula,
        "celular": celular,
        "correo": correo,
    }
    clientes = servicios(request).clientes
    try:
        cliente = clientes.registrar(**datos)
    except exc.ErrorDeNegocio as error:
        contexto = {"datos": datos, "dominio": clientes.dominio_correo, "error": error.mensaje}
        return mostrar(request, "cliente/registro.html", contexto, status_code=422)
    request.session["cliente_id"] = cliente.id
    avisar(request, f"Te registraste con el código de cliente {cliente.codigo}. Ya puedes pedir.")
    return redirigir("/")


@router.post("/salir")
def salir(request: Request) -> Response:
    """Cierra la sesión del cliente."""
    request.session.pop("cliente_id", None)
    request.session.pop("borrador", None)
    return redirigir("/")
