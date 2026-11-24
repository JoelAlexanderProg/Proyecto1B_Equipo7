# 7. Manual de instalación · CaféPoli 1.0.0

Para la persona encargada de instalar y mantener CaféPoli en el equipo de la cafetería. La forma
recomendada es con Docker: el mismo entorno en cualquier equipo y un solo comando.

## 7.1 Requisitos

| Elemento | Requisito |
|---|---|
| Sistema operativo | Windows 10/11, macOS o Linux de 64 bits |
| Docker | Docker Desktop, o Docker Engine con el complemento Compose v2 |
| Memoria y disco | 512 MB libres de RAM (el contenedor usa hasta 256 MB) y 1 GB de disco |
| Red | Puerto 8000 libre; para pedir desde los celulares, todos en la misma red que el equipo |
| Navegador de los usuarios | Chrome, Edge, Firefox o Safari actuales, en celular o computadora |
| Solo para la instalación sin Docker | Python 3.12 |

## 7.2 Obtener el código

```powershell
git clone --branch v1.0.0 https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7.git
cd Proyecto1B_Equipo7
```

Sin Git, descarga el archivo *Source code (zip)* de la
[release v1.0.0](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/releases/tag/v1.0.0) y
descomprímelo.

## 7.3 Configurar

1. Copia la plantilla de configuración:

   ```powershell
   copy .env.example .env        # en macOS o Linux: cp .env.example .env
   ```

2. Abre `.env` con un editor y define al menos:

   | Variable | Qué poner |
   |---|---|
   | `CAFETERIA_CLAVE_PERSONAL` | La clave del personal, de 8 caracteres o más. **Obligatoria** |
   | `CAFETERIA_SECRETO_SESION` | Un texto aleatorio largo, para que las sesiones sobrevivan a los reinicios. Se puede generar con `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
   | `CAFETERIA_USUARIO_PERSONAL` | El usuario del personal (por defecto `personal`) |
   | `CAFETERIA_DOMINIO_CORREO` | El dominio del correo institucional (por defecto `epn.edu.ec`) |

   El archivo `.env` contiene la clave: no lo compartas ni lo subas a un repositorio.

## 7.4 Instalar y ejecutar con Docker

```powershell
docker compose up -d --build
```

El comando construye la imagen `cafeteria-app:1.0.0`, crea el volumen `cafeteria-data` para la base
de datos y arranca el contenedor `cafepoli`. La primera vez tarda unos minutos.

**Verificar la instalación:**

```powershell
docker compose ps                        # la columna STATUS debe decir (healthy)
curl http://localhost:8000/health        # {"estado":"ok","version":"1.0.0"}
```

| Dirección | Para |
|---|---|
| `http://localhost:8000` | Clientes: menú y pedidos |
| `http://localhost:8000/personal` | Personal: tablero y menú |
| `http://localhost:8000/docs` | Documentación de la API |

**Acceso desde los celulares.** Busca la dirección IP del equipo (`ipconfig` en Windows, junto a
«Dirección IPv4») y abre `http://<esa-ip>:8000` desde un celular conectado a la misma red. Si no
carga, permite el puerto 8000 en el cortafuegos del sistema.

El menú de demostración (10 productos) se carga solo la primera vez, cuando la base está vacía.
Para empezar con el menú vacío, pon `CAFETERIA_CARGAR_SEMILLA=0` en `.env` antes de la primera
ejecución.

## 7.5 Operación

| Tarea | Comando |
|---|---|
| Ver los registros | `docker compose logs -f` |
| Detener | `docker compose stop` |
| Iniciar de nuevo | `docker compose start` |
| Aplicar cambios de `.env` | `docker compose up -d` |
| Actualizar a una versión nueva | `git fetch --tags`, `git checkout vX.Y.Z` y `docker compose up -d --build` |
| Detener y quitar el contenedor, **conservando los datos** | `docker compose down` |
| Quitar todo, **incluidos los datos** | `docker compose down -v` |

El contenedor se reinicia solo si se cae (`restart: unless-stopped`), salvo que lo hayas detenido a
mano. Docker comprueba su salud cada 30 segundos contra `/health`.

### Respaldo de la base de datos

Con el servicio en marcha, crea una copia consistente y llévala al equipo:

```powershell
docker exec cafepoli python -c "import sqlite3; o=sqlite3.connect('/app/data/cafeteria.db'); d=sqlite3.connect('/app/data/respaldo.db'); o.backup(d); d.close()"
docker cp cafepoli:/app/data/respaldo.db .\respaldo-AAAA-MM-DD.db
```

### Restauración

Con el servicio en marcha, copia el respaldo dentro del contenedor y restáuralo con la misma API
de SQLite:

```powershell
docker cp .\respaldo-AAAA-MM-DD.db cafepoli:/tmp/respaldo.db
docker exec cafepoli python -c "import sqlite3; r=sqlite3.connect('/tmp/respaldo.db'); d=sqlite3.connect('/app/data/cafeteria.db'); r.backup(d); d.close()"
```

> No reemplaces el archivo con `docker cp` directamente sobre `/app/data/cafeteria.db`. El archivo
> copiado queda como propiedad de `root`, y la aplicación, que corre como el usuario `cafeteria`,
> ya no puede escribir: «attempt to write a readonly database». Lo detectamos al probar este
> manual ([defectos](06-pruebas/defectos.md#hallazgo-al-probar-el-manual-de-instalación)).

## 7.6 Instalación sin Docker (desarrollo o prueba)

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .            # agrega ".[dev]" para pruebas y Ruff
.venv\Scripts\python -m cafeteria                   # lee .env; http://127.0.0.1:8000
```

En macOS o Linux usa `.venv/bin/python`. Por defecto escucha solo en el propio equipo
(`CAFETERIA_HOST=127.0.0.1`). Para que la usen los celulares, define `CAFETERIA_HOST=0.0.0.0`.

## 7.7 Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| El contenedor se reinicia una y otra vez y el registro dice «Define CAFETERIA_CLAVE_PERSONAL…» | Falta `.env` o la clave tiene menos de 8 caracteres | Completa `.env` y ejecuta `docker compose up -d` |
| `Bind for 0.0.0.0:8000 failed: port is already allocated` | Otro programa usa el puerto 8000 | Cambia `"8000:8000"` por `"8080:8000"` en `compose.yaml` y usa `http://localhost:8080` |
| `docker compose ps` muestra `(unhealthy)` | La aplicación no responde | Revisa `docker compose logs` y reinicia con `docker compose restart` |
| Los celulares no abren la página | Red distinta o cortafuegos | Misma red Wi-Fi; permite el puerto 8000 en el cortafuegos |
| Las sesiones se cierran cada vez que se reinicia | `CAFETERIA_SECRETO_SESION` vacío | Define un secreto fijo en `.env` |
| El personal olvidó la clave | — | Cambia `CAFETERIA_CLAVE_PERSONAL` en `.env` y ejecuta `docker compose up -d` |
| «attempt to write a readonly database» | Se restauró la base con `docker cp` directo | Usa el procedimiento de restauración de la sección 7.5, o `docker exec -u root cafepoli chown cafeteria:cafeteria /app/data/cafeteria.db` |
