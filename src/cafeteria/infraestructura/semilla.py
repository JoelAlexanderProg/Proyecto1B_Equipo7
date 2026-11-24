"""Menú de demostración que se carga cuando la base de datos está vacía."""

from cafeteria.aplicacion.servicios import ServicioMenu
from cafeteria.dominio.modelos import Categoria

MENU_INICIAL = (
    ("Bolón de verde con queso", Categoria.ALIMENTO, "1.75", True),
    ("Empanada de viento", Categoria.ALIMENTO, "0.80", True),
    ("Sánduche de pollo", Categoria.ALIMENTO, "1.50", True),
    ("Humita", Categoria.ALIMENTO, "1.00", False),
    ("Almuerzo del día", Categoria.ALIMENTO, "3.00", True),
    ("Café pasado", Categoria.BEBIDA, "0.75", True),
    ("Capuchino", Categoria.BEBIDA, "1.50", True),
    ("Colada morada", Categoria.BEBIDA, "1.25", True),
    ("Jugo de mora", Categoria.BEBIDA, "1.00", True),
    ("Agua sin gas", Categoria.BEBIDA, "0.60", True),
)


def cargar_menu_inicial(menu: ServicioMenu) -> int:
    """Registra el menú de demostración si todavía no hay productos.

    Args:
        menu: servicio del menú.

    Returns:
        int: cantidad de productos registrados (0 si el menú ya tenía productos).
    """
    if menu.listar():
        return 0
    for nombre, categoria, precio, disponible in MENU_INICIAL:
        menu.registrar(nombre=nombre, categoria=categoria, precio=precio, disponible=disponible)
    return len(MENU_INICIAL)
