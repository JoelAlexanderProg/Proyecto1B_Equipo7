# CaféPoli

Pedidos anticipados, seguimiento y retiro con código para la cafetería universitaria.
Proyecto IB de ISWD633 Construcción y Evolución de Software (EPN, 2026-B), Equipo 7.

- **Cliente**: consulta el menú, arma su pedido con el total a la vista, lo confirma y recibe un
  código de retiro (por ejemplo `K7P-4QX`) con el que sigue el estado del pedido.
- **Personal**: ve los pedidos por estado, registra su avance y entrega el pedido solo si el
  código que presenta el cliente coincide. También mantiene el menú, sus precios y su
  disponibilidad.

## Inicio rápido con Docker

Requisitos: Docker Desktop (o Docker Engine con Compose).

```powershell
copy .env.example .env      # y define CAFETERIA_CLAVE_PERSONAL
docker compose up -d --build
```

Abre <http://localhost:8000>. Los datos se guardan en el volumen `cafeteria-data`, así que
sobreviven a `docker compose down` y a reconstruir la imagen. El contenedor tiene healthcheck
contra `/health`, se reinicia solo si se cae (`unless-stopped`) y tiene límites de 256 MB de
memoria y media CPU.

## Inicio rápido (local)

Requisitos: Python 3.12.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
copy .env.example .env      # y define CAFETERIA_CLAVE_PERSONAL
.venv\Scripts\python -m cafeteria
```

Abre <http://127.0.0.1:8000>. El tablero del personal está en `/personal` y la documentación
de la API en `/docs`.

## Pruebas

```powershell
.venv\Scripts\python -m pytest --cov
.venv\Scripts\ruff check src tests
```

## Estructura

```text
src/cafeteria/
├── dominio/          entidades y reglas de negocio RN-NEG-01 a 07
├── aplicacion/       servicios (casos de uso) y puertos de persistencia
├── infraestructura/  SQLite, repositorios y menú de demostración
└── presentacion/     rutas web y API (FastAPI), plantillas y estilos
tests/  unit/ · integracion/ · sistema/
```

La documentación completa del proyecto (requisitos, diseño, pruebas y manuales) está en la
rama [`documentacion`](../../tree/documentacion).
