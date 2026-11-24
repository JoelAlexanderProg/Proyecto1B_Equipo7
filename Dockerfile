# Imagen de CaféPoli. Construcción: docker build -t cafeteria-app:1.0.0 .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CAFETERIA_HOST=0.0.0.0 \
    CAFETERIA_PUERTO=8000 \
    CAFETERIA_BD=/app/data/cafeteria.db

WORKDIR /app

# Usuario sin privilegios: el proceso no se ejecuta como root.
RUN useradd --create-home --uid 1000 cafeteria

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install . \
    && mkdir -p /app/data \
    && chown cafeteria:cafeteria /app/data

USER cafeteria
EXPOSE 8000

# La base SQLite vive en un volumen para que los datos sobrevivan al contenedor.
VOLUME ["/app/data"]

# La imagen slim no trae curl: el chequeo usa Python contra /health.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)" || exit 1

# Proceso principal en primer plano para que Docker pueda monitorearlo.
CMD ["python", "-m", "cafeteria"]
