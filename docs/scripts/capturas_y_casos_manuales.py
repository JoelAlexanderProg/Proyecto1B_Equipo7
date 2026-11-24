"""Capturas de los manuales y ejecución asistida de los casos manuales CT-M01, CT-M02 y CT-M05.

Requiere una instancia de CaféPoli con la base vacía (solo el menú de demostración) y Playwright:

    python -m pip install playwright==1.58.0 && python -m playwright install chromium
    python docs/scripts/capturas_y_casos_manuales.py http://127.0.0.1:8001 <clave-del-personal>

Guarda las capturas en docs/img y los resultados medidos en docs/06-pruebas/evidencias/casos-manuales.json.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE, CLAVE = sys.argv[1].rstrip("/"), sys.argv[2]
DOCS = Path(__file__).resolve().parents[1]
IMG = DOCS / "img"
IMG.mkdir(exist_ok=True)
resultados: dict[str, dict] = {}


def captura(pag: Page, nombre: str, completa: bool = True) -> None:
    pag.screenshot(path=IMG / f"{nombre}.png", full_page=completa)


def medir_movil(pag: Page, pagina: str) -> dict:
    """CT-M01: sin desplazamiento horizontal y objetivos táctiles de al menos 44 px."""
    pag.wait_for_load_state("load")
    return pag.evaluate(
        """(pagina) => {
            const ancho = document.documentElement.scrollWidth <= window.innerWidth;
            const selector = 'button, .boton, input:not([type=hidden]), .barra a, .volver, summary';
            const toques = [...document.querySelectorAll(selector)]
                .filter(e => e.offsetParent !== null)
                .map(e => ({texto: (e.innerText || e.getAttribute('aria-label') || e.tagName).trim().slice(0, 40),
                            alto: Math.round(e.getBoundingClientRect().height)}));
            const altos = toques.map(t => t.alto);
            return {pagina, sin_desplazamiento_horizontal: ancho, controles: toques.length,
                    alto_minimo_px: Math.min(...altos), menores_de_44: toques.filter(t => t.alto < 44)};
        }""",
        pagina,
    )


def registrar(pag: Page, nombre, apellido, cedula, celular, correo, capturar=False) -> None:
    pag.goto(BASE + "/registro")
    for campo, valor in (("#nombre", nombre), ("#apellido", apellido), ("#cedula", cedula),
                         ("#celular", celular), ("#correo", correo)):
        pag.fill(campo, valor)
    if capturar:
        captura(pag, "u02_registro")
    pag.click("button[type=submit]")


def pedir(pag: Page, *productos: str) -> str:
    pag.goto(BASE + "/")
    for nombre in productos:
        pag.click(f"[aria-label='Agregar uno: {nombre}']")
    pag.click("text=Revisar pedido")
    pag.click("text=Confirmar pedido")
    return pag.url.rsplit("/", 1)[1]


with sync_playwright() as p:
    nav = p.chromium.launch()

    # ---- Cliente en un celular de 390 px ----
    movil = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    cli = movil.new_page()
    cli.goto(BASE + "/")
    captura(cli, "u01_menu_publico")
    registrar(cli, "Ana", "Pérez", "1710034065", "0991234567", "ana.perez@epn.edu.ec", capturar=True)
    for nombre in ("Bolón de verde con queso", "Empanada de viento", "Empanada de viento", "Café pasado"):
        cli.click(f"[aria-label='Agregar uno: {nombre}']")
    captura(cli, "u03_menu_carrito", completa=False)
    total_en_vivo = cli.inner_text("#carrito-total")
    cli.click("text=Revisar pedido")
    captura(cli, "u04_revision")
    cli.click("text=Confirmar pedido")
    codigo_ana = cli.url.rsplit("/", 1)[1]
    captura(cli, "u05_ticket")
    cli.goto(BASE + "/")
    cli.click("text=Revisar pedido")
    captura(cli, "u08_error_pedido_vacio", completa=False)

    # CT-M01 a 360 px: medición en cada pantalla del cliente
    angosto = nav.new_context(viewport={"width": 360, "height": 740})
    a = angosto.new_page()
    medidas = []
    a.goto(BASE + "/")
    medidas.append(medir_movil(a, "menú público"))
    registrar(a, "Luis", "Cruz", "0102030400", "0987654321", "luis.cruz@epn.edu.ec")
    medidas.append(medir_movil(a, "menú con sesión"))
    a.click("[aria-label='Agregar uno: Capuchino']")
    a.click("text=Revisar pedido")
    medidas.append(medir_movil(a, "revisión"))
    a.click("text=Confirmar pedido")
    medidas.append(medir_movil(a, "ticket"))
    a.goto(BASE + "/mis-pedidos")
    medidas.append(medir_movil(a, "mis pedidos"))
    resultados["CT-M01"] = {"total_en_vivo_tras_4_articulos": total_en_vivo, "pantallas_360px": medidas}

    # Más pedidos de otro cliente para poblar el tablero
    for productos in (("Almuerzo del día", "Agua sin gas"), ("Sánduche de pollo", "Jugo de mora"),
                      ("Colada morada", "Empanada de viento")):
        pedir(a, *productos)

    # ---- Personal en una pantalla de 1280 px ----
    escritorio = nav.new_context(viewport={"width": 1280, "height": 860})
    per = escritorio.new_page()
    per.goto(BASE + "/personal/ingresar")
    per.fill("#usuario", "personal")
    per.fill("#clave", CLAVE)
    captura(per, "p01_ingreso", completa=False)
    per.click("button[type=submit]")

    def tarjeta(codigo):
        return per.locator("article.orden", has_text=codigo)

    tarjeta(codigo_ana).locator("button").click()
    tarjeta(codigo_ana).locator("button").click()
    codigos = per.locator(".orden-codigo").all_inner_texts()
    tarjeta(codigos[0]).locator("button").click()
    captura(per, "p02_tablero")
    resumen = per.locator(".resumen").inner_text()

    # Cliente ve su pedido listo
    cli.goto(BASE + f"/pedidos/{codigo_ana}")
    captura(cli, "u07_ticket_listo")

    tarjeta(codigo_ana).locator("input[name=codigo]").fill("ABC-DEF")
    tarjeta(codigo_ana).locator("button").click()
    captura(per, "p03_entrega_codigo_incorrecto", completa=False)
    aviso_error = per.locator(".aviso").inner_text()
    tarjeta(codigo_ana).locator("input[name=codigo]").fill(codigo_ana.lower().replace("-", ""))
    tarjeta(codigo_ana).locator("button").click()
    captura(per, "p04_entrega_correcta", completa=False)
    aviso_ok = per.locator(".aviso").inner_text()
    resultados["CT-M02"] = {"resumen_tablero": resumen, "aviso_codigo_incorrecto": aviso_error,
                            "aviso_entrega": aviso_ok}

    cli.goto(BASE + "/mis-pedidos")
    captura(cli, "u06_mis_pedidos")

    per.goto(BASE + "/personal/menu")
    captura(per, "p05_menu")
    per.click("tr:has-text('Café pasado') >> text=Editar")
    captura(per, "p06_editar_producto", completa=False)

    # CT-M05: la recarga automática no interrumpe la escritura de un código
    per.goto(BASE + "/personal")
    while per.locator("input[name=codigo]").count() == 0:
        per.locator("article.orden form button").first.click()
    per.evaluate("window.__sinRecargar = true")
    entrada = per.locator("input[name=codigo]").first
    entrada.fill("K7P")
    per.wait_for_timeout(25_000)
    conserva = per.evaluate("window.__sinRecargar === true") and entrada.input_value() == "K7P"
    entrada.fill("")
    per.locator("h1").click()
    per.wait_for_timeout(25_000)
    recargo = per.evaluate("window.__sinRecargar === undefined")
    resultados["CT-M05"] = {"conserva_lo_escrito_tras_25s": conserva, "recarga_sin_escritura_tras_25s": recargo}

    nav.close()

salida = DOCS / "06-pruebas" / "evidencias" / "casos-manuales.json"
salida.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(resultados, ensure_ascii=False, indent=2))
