# 3. Ambiente de desarrollo

Herramientas, versiones y configuración con que se construyó y verificó el Release 1.0. El
[flujo de trabajo](flujo-de-trabajo.md) describe la estrategia de ramificación y la gestión de la
configuración.

## 3.1 Herramientas seleccionadas

| Herramienta | Versión | Uso | Por qué |
|---|---|---|---|
| Python | 3.12.10 | Lenguaje | El equipo lo domina; ecosistema web y de pruebas maduro (ADR-001) |
| FastAPI · Starlette | 0.165.0 · 1.10.0 | Framework web | Documentación OpenAPI automática, formularios y `TestClient` |
| Uvicorn | 0.54.0 | Servidor ASGI | Servidor de referencia de FastAPI |
| Jinja2 | 3.1.6 | Plantillas HTML | Herencia de plantillas: evita código duplicado en las páginas |
| SQLite (`sqlite3`) | 3.x de la biblioteca estándar | Persistencia | Sin servicios adicionales; un archivo en un volumen (ADR-003) |
| pytest · pytest-cov · coverage | 9.2.0 · 7.1.0 · 7.17.5 | Pruebas y cobertura | Parametrización para particiones de equivalencia; reporte XML para SonarQube |
| httpx2 | 2.16.2 | Cliente HTTP de `TestClient` | Reemplaza a `httpx`, que Starlette 1.10 marca como obsoleto |
| Ruff | 0.17.6 | Linter y formateador | Verifica PEP 8 [11] y el orden de los *imports* en milisegundos |
| SonarQube Community Build | 26.11.0 | Análisis estático | Perfil *Sonar way comprehensive*, Quality Gate y deuda técnica |
| SonarScanner CLI | 8.5.0 | Envío del análisis | Contenedor en la red `net-sonar`, como en TG3 |
| Docker Desktop · Compose | 29.9.3 | Contenedores | Mismo entorno en desarrollo y en la cafetería («en mi máquina funciona», semana 2) |
| Git · GitHub · GitHub CLI | 2.56.0 · 2.105.0 | Control de versiones | Ramas, Issues, PR, etiquetas y *releases* desde la terminal |
| GitHub Actions | `ubuntu-latest` | Integración continua | Ruff, pytest y construcción de la imagen en cada PR |
| pdoc | 16.0.0 | Documentación técnica | Genera HTML navegable desde los docstrings (equivalente a JavaDoc) |
| Playwright · Chromium | 1.58.0 | Capturas y revisión visual | Capturas reproducibles para los manuales y la revisión de la interfaz |
| Visual Studio Code | 1.145.3 | Editor | Integración con Git, Python y Docker |
| Agente de IA (Claude Code) | — | Apoyo | Asistencia en programación, pruebas y redacción, dentro de los ámbitos del sílabo |

Las versiones de las dependencias de Python están fijadas en `pyproject.toml`, para que cualquier
integrante o la CI obtenga exactamente el mismo entorno.

## 3.2 Preparar el entorno

```powershell
git clone https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7.git
cd Proyecto1B_Equipo7
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"   # app + pytest, cobertura, Ruff
copy .env.example .env                            # definir CAFETERIA_CLAVE_PERSONAL
.venv\Scripts\python -m cafeteria                 # http://127.0.0.1:8000
```

Comandos de verificación, los mismos que ejecuta la CI:

```powershell
.venv\Scripts\ruff check src tests
.venv\Scripts\ruff format --check src tests
.venv\Scripts\python -m pytest --cov
```

## 3.3 Estructura del repositorio

```text
Proyecto1B_Equipo7/
├── src/cafeteria/
│   ├── dominio/            entidades y reglas (sin dependencias externas)
│   ├── aplicacion/         servicios y puertos
│   ├── infraestructura/    SQLite, repositorios, menú de demostración
│   ├── presentacion/       rutas, plantillas, CSS, JS y fuentes
│   ├── config.py           configuración por variables de entorno
│   └── __main__.py         arranque: python -m cafeteria
├── tests/  unit/ · integracion/ · sistema/
├── .github/  workflows/ci.yml · ISSUE_TEMPLATE/ · pull_request_template.md
├── Dockerfile · compose.yaml · .dockerignore · .env.example
├── pyproject.toml          dependencias fijadas, pytest, coverage y Ruff
├── sonar-project.properties
└── README.md · CONTRIBUTING.md · CHANGELOG.md
```

En la rama `documentacion` se agrega `docs/` con estos entregables.

## 3.4 Configuración

| Variable | Propósito | Valor por defecto |
|---|---|---|
| `CAFETERIA_CLAVE_PERSONAL` | Clave de la cuenta del personal (obligatoria, ≥ 8 caracteres) | — |
| `CAFETERIA_USUARIO_PERSONAL` | Usuario de la cuenta del personal | `personal` |
| `CAFETERIA_SECRETO_SESION` | Firma de las cookies de sesión | Aleatorio en cada arranque |
| `CAFETERIA_BD` | Archivo SQLite | `data/cafeteria.db` (`/app/data/cafeteria.db` en Docker) |
| `CAFETERIA_DOMINIO_CORREO` | Dominio del correo de los clientes | `epn.edu.ec` |
| `CAFETERIA_CARGAR_SEMILLA` | Cargar el menú de demostración si la base está vacía | `1` |
| `CAFETERIA_HOST` · `CAFETERIA_PUERTO` | Dirección del servidor | `127.0.0.1` · `8000` |

Las variables separan la configuración del código, pero no son un almacén seguro de secretos
(semana 3 [6]). Por eso `.env` está en `.gitignore` y `.env.example` documenta cada variable sin
valores reales.

## 3.5 Integración continua

`.github/workflows/ci.yml` se ejecuta en cada Pull Request y en cada push a `main`:

| Trabajo | Pasos | Falla si |
|---|---|---|
| Ruff y pytest | `pip install -e ".[dev]"`, `ruff check`, `ruff format --check`, `pytest --cov` (sube `coverage.xml`) | Hay observaciones de estilo o falla una prueba |
| Construcción de la imagen | `docker build` | El Dockerfile no construye |

Desde el 24-11-2026, `main` está protegida: no se puede integrar sin PR ni con alguno de los dos
trabajos en rojo ([incidente INC-01](flujo-de-trabajo.md#310-incidente-inc-01)).
