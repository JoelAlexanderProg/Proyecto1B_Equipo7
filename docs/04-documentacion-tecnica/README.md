# 4. Documentación técnica del código

El código se documenta en tres niveles, siguiendo la semana 5 [6]:

1. **Nombres y estructura.** Nombres que revelan la intención, en el idioma de la especificación
   (`Pedido.entregar`, `CodigoRetiroIncorrecto`).
2. **Docstrings.** Contratos de cada módulo, clase y función pública, con sus parámetros, su
   resultado y sus excepciones.
3. **Referencia generada.** Un sitio HTML navegable a partir de los docstrings y la especificación
   OpenAPI de la API.

## 4.1 Docstrings: equivalencia con JavaDoc

Se usa el estilo Google sobre PEP 257 [12]. Cada sección cumple el papel de una etiqueta de JavaDoc:

| JavaDoc | Docstring de Python | Contenido |
|---|---|---|
| Descripción | Primera línea y párrafo | Qué hace y, cuando no es evidente, por qué |
| `@param` | `Args:` | Finalidad y restricciones de cada parámetro |
| `@return` | `Returns:` | Tipo y significado del resultado |
| `@throws` | `Raises:` | Excepción y condición en que ocurre |
| `@see` | Referencia en el texto | Regla o supuesto relacionado (`RN-NEG-07`, `A7`) |

Ejemplo real (`src/cafeteria/dominio/modelos.py`):

```python
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
```

Los comentarios dentro del código explican **decisiones**, no lo evidente. Por ejemplo: por qué
el estado avanza con una tabla y no con condicionales, por qué los montos se guardan en centavos o
por qué el healthcheck usa Python en lugar de `curl`.

**Cobertura de la documentación:** 179 elementos públicos (módulos, clases y funciones),
**179 documentados** en la versión 1.0.0. Se mide recorriendo el árbol sintáctico con `ast`.

## 4.2 Referencia HTML (equivalente a JavaDoc)

Generada con pdoc 16 desde los docstrings: [`html/cafeteria.html`](html/cafeteria.html). Incluye
los módulos, las clases con sus atributos, las firmas con anotaciones de tipo y el código fuente de
cada función. Para verla, clona la rama `documentacion` y abre el archivo en un navegador.

Para regenerarla:

```powershell
.venv\Scripts\python -m pip install pdoc==16.0.0
.venv\Scripts\python -m pdoc cafeteria -o docs/04-documentacion-tecnica/html --docformat google
```

| Paquete | Contenido |
|---|---|
| `cafeteria.dominio` | `modelos` (entidades, reglas, estados), `codigo_retiro`, `validaciones`, `excepciones` |
| `cafeteria.aplicacion` | `servicios` (casos de uso), `puertos` (protocolos de repositorio) |
| `cafeteria.infraestructura` | `basedatos` (esquema, conexión), `repositorios` (SQLite), `semilla` |
| `cafeteria.presentacion` | `web` (fábrica de la app), `rutas_cliente`, `rutas_personal`, `rutas_api`, `plantillas`, `dependencias` |
| `cafeteria.config` | Configuración por variables de entorno |

## 4.3 API

FastAPI genera la especificación OpenAPI 3.1 desde el código. Con la aplicación en ejecución se
consulta de forma interactiva en `http://localhost:8000/docs`; la copia de esta versión está en
[`openapi.json`](openapi.json).

| Operación | Respuesta | Uso |
|---|---|---|
| `GET /health` | `{"estado": "ok", "version": "1.0.0"}` | Healthcheck del contenedor (RNF-07) |
| `GET /api/v1/productos?disponibles=true` | Lista de `{codigo, nombre, categoria, precio, disponible}`; el precio es texto decimal (`"1.75"`) para no perder precisión | Consulta del menú (RU-01) |

Errores: las rutas inexistentes bajo `/api/` responden `404` con `{"detail": "Not Found"}`. La
versión de la API va en la ruta (`/api/v1`): un cambio incompatible publicaría `/api/v2` sin romper
a los clientes existentes.

## 4.4 Instrucciones para construir y ejecutar

Están en el `README.md` de `main` (inicio rápido con Docker y en local) y, con detalle, en el
[manual de instalación](../07-manual-instalacion.md).
