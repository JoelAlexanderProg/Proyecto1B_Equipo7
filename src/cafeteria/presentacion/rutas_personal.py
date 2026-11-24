"""Páginas del personal: ingreso, tablero de pedidos y mantenimiento del menú (PN-02)."""

from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from cafeteria.dominio import excepciones as exc
from cafeteria.presentacion.dependencias import es_personal, servicios
from cafeteria.presentacion.plantillas import avisar, mostrar, redirigir

RUTA_TABLERO = "/personal"
RUTA_INGRESO_PERSONAL = "/personal/ingresar"
RUTA_MENU_PERSONAL = "/personal/menu"

router = APIRouter(prefix=RUTA_TABLERO, include_in_schema=False)

Campo = Annotated[str, Form()]
RECARGA_TABLERO = 20
"""Segundos entre recargas automáticas del tablero."""


def _sin_acceso(request: Request) -> Response | None:
    """Devuelve una redirección al ingreso si la sesión no es del personal."""
    return None if es_personal(request) else redirigir(RUTA_INGRESO_PERSONAL)


@router.get("/ingresar", response_class=HTMLResponse)
def formulario_ingreso(request: Request) -> HTMLResponse:
    """Formulario de ingreso del personal (HU-11)."""
    return mostrar(request, "personal/ingresar.html", {"usuario": ""})


@router.post("/ingresar")
def ingresar(request: Request, usuario: Campo = "", clave: Campo = "") -> Response:
    """Verifica la cuenta del personal y marca la sesión."""
    try:
        servicios(request).acceso.verificar(usuario, clave)
    except exc.CredencialesInvalidas as error:
        contexto = {"usuario": usuario, "error": error.mensaje}
        return mostrar(request, "personal/ingresar.html", contexto, status_code=422)
    request.session.pop("cliente_id", None)
    request.session["personal"] = True
    return redirigir(RUTA_TABLERO)


@router.post("/salir")
def salir(request: Request) -> Response:
    """Cierra la sesión del personal."""
    request.session.pop("personal", None)
    return redirigir(RUTA_INGRESO_PERSONAL)


@router.get("", response_class=HTMLResponse)
def tablero(request: Request) -> Response:
    """Pedidos en curso agrupados por estado, del más antiguo al más reciente (HU-08)."""
    if respuesta := _sin_acceso(request):
        return respuesta
    s = servicios(request)
    columnas = s.pedidos.tablero()
    ids = {pedido.cliente_id for pedidos in columnas.values() for pedido in pedidos}
    contexto = {
        "seccion": "pedidos",
        "columnas": columnas,
        "clientes": {cliente_id: s.clientes.obtener(cliente_id) for cliente_id in ids},
        "entregados_hoy": s.pedidos.entregados_hoy(),
        "recarga": RECARGA_TABLERO,
    }
    return mostrar(request, "personal/tablero.html", contexto)


@router.post("/pedidos/{pedido_id}/avanzar")
def avanzar(request: Request, pedido_id: int) -> Response:
    """Registra el avance de un pedido: Pendiente → En preparación → Listo (HU-09)."""
    if respuesta := _sin_acceso(request):
        return respuesta
    try:
        pedido = servicios(request).pedidos.avanzar(pedido_id)
        avisar(request, f"Pedido {pedido.codigo_retiro}: {pedido.estado.etiqueta}.")
    except exc.ErrorDeNegocio as error:
        avisar(request, error.mensaje, "error")
    return redirigir(RUTA_TABLERO)


@router.post("/pedidos/{pedido_id}/entregar")
def entregar(request: Request, pedido_id: int, codigo: Campo = "") -> Response:
    """Registra la entrega si el código presentado coincide (HU-10, RN-NEG-07)."""
    if respuesta := _sin_acceso(request):
        return respuesta
    pedidos = servicios(request).pedidos
    try:
        pedido = pedidos.entregar(pedido_id, codigo)
        avisar(request, f"Pedido {pedido.codigo_retiro} entregado.")
    except exc.PedidoNoEncontrado:
        raise HTTPException(404) from None
    except exc.ErrorDeNegocio as error:
        codigo_pedido = pedidos.obtener(pedido_id).codigo_retiro
        avisar(
            request, f"Pedido {codigo_pedido}: no se registró la entrega. {error.mensaje}", "error"
        )
    return redirigir(RUTA_TABLERO)


def _formulario_producto(contexto: dict, request: Request, status_code: int = 200) -> Response:
    plantilla = "personal/producto.html" if "producto" in contexto else "personal/menu.html"
    if plantilla == "personal/menu.html":
        contexto.setdefault("productos", servicios(request).menu.listar())
    return mostrar(request, plantilla, {"seccion": "menu", **contexto}, status_code)


@router.get("/menu", response_class=HTMLResponse)
def menu(request: Request) -> Response:
    """Lista de productos y formulario para agregar uno nuevo (HU-07)."""
    if respuesta := _sin_acceso(request):
        return respuesta
    return _formulario_producto({"datos": {"disponible": "1"}}, request)


@router.post("/menu")
def registrar_producto(
    request: Request,
    nombre: Campo = "",
    categoria: Campo = "",
    precio: Campo = "",
    disponible: Campo = "",
) -> Response:
    """Agrega un producto al menú con un código asignado por el sistema."""
    if respuesta := _sin_acceso(request):
        return respuesta
    try:
        producto = servicios(request).menu.registrar(
            nombre=nombre, categoria=categoria, precio=precio, disponible=bool(disponible)
        )
    except exc.ErrorDeNegocio as error:
        datos = {
            "nombre": nombre,
            "categoria": categoria,
            "precio": precio,
            "disponible": disponible,
        }
        return _formulario_producto({"datos": datos, "error": error.mensaje}, request, 422)
    avisar(request, f"{producto.nombre} se agregó al menú con el código {producto.codigo}.")
    return redirigir(RUTA_MENU_PERSONAL)


@router.get("/menu/{codigo}", response_class=HTMLResponse)
def editar_producto(request: Request, codigo: str) -> Response:
    """Formulario para cambiar nombre, categoría, precio y disponibilidad."""
    if respuesta := _sin_acceso(request):
        return respuesta
    try:
        producto = servicios(request).menu.obtener(codigo)
    except exc.ProductoNoEncontrado:
        raise HTTPException(404) from None
    datos = {
        "nombre": producto.nombre,
        "categoria": producto.categoria.value,
        "precio": str(producto.precio).replace(".", ","),
        "disponible": "1" if producto.disponible else "",
    }
    return _formulario_producto({"producto": producto, "datos": datos}, request)


@router.post("/menu/{codigo}")
def actualizar_producto(
    request: Request,
    codigo: str,
    nombre: Campo = "",
    categoria: Campo = "",
    precio: Campo = "",
    disponible: Campo = "",
) -> Response:
    """Guarda los cambios del producto; los pedidos confirmados conservan su precio."""
    if respuesta := _sin_acceso(request):
        return respuesta
    menu_servicio = servicios(request).menu
    try:
        producto = menu_servicio.actualizar(
            codigo, nombre=nombre, categoria=categoria, precio=precio, disponible=bool(disponible)
        )
    except exc.ProductoNoEncontrado:
        raise HTTPException(404) from None
    except exc.ErrorDeNegocio as error:
        datos = {
            "nombre": nombre,
            "categoria": categoria,
            "precio": precio,
            "disponible": disponible,
        }
        contexto = {
            "producto": menu_servicio.obtener(codigo),
            "datos": datos,
            "error": error.mensaje,
        }
        return _formulario_producto(contexto, request, 422)
    avisar(request, f"Se guardaron los cambios de {producto.nombre}.")
    return redirigir(RUTA_MENU_PERSONAL)


@router.post("/menu/{codigo}/disponibilidad")
def cambiar_disponibilidad(request: Request, codigo: str, disponible: Campo = "") -> Response:
    """Marca un producto como disponible o no disponible (RN-NEG-02)."""
    if respuesta := _sin_acceso(request):
        return respuesta
    try:
        producto = servicios(request).menu.cambiar_disponibilidad(codigo, disponible == "1")
    except exc.ProductoNoEncontrado:
        raise HTTPException(404) from None
    estado = "disponible" if producto.disponible else "no disponible"
    avisar(request, f"{producto.nombre} ahora está {estado}.")
    return redirigir(RUTA_MENU_PERSONAL)
