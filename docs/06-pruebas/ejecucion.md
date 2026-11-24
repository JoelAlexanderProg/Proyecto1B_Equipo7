# Ejecución de las pruebas · versión 1.0.0

## Pruebas automatizadas

| Ejecución | Fecha | Código | Total | Aprobadas | Fallidas | Cobertura | Evidencia |
|---|---|---|---|---|---|---|---|
| Local (Windows) | 24-11-2026 09:57 | `v1.0.0` (`46a63f9`) | 113 | 113 | 0 | 97 % (líneas y ramas) | [reporte JUnit](evidencias/reporte-pytest.xml) · [cobertura HTML](evidencias/cobertura/index.html) |
| CI (Linux) | 24-11-2026 14:57 UTC | `46a63f9` | 113 | 113 | 0 | `coverage.xml` | [ejecución 45419809912](../../../../actions/runs/45419809912) |

| Nivel | Archivo | Ejecuciones |
|---|---|---|
| Unitaria | `tests/unit/test_pedido.py` | 32 |
| Unitaria | `tests/unit/test_codigo_y_validaciones.py` | 25 |
| Unitaria | `tests/unit/test_config.py` | 3 |
| Integración | `tests/integracion/test_servicios.py` | 17 |
| Sistema | `tests/sistema/test_web_cliente.py` | 21 |
| Sistema | `tests/sistema/test_web_personal.py` | 15 |

El resultado de cada caso `CT-XX.Y` está en el [catálogo](casos-de-prueba.md).

**Historia de las pruebas automatizadas.** Ninguna prueba automatizada falló en su primera
ejecución: se escribieron desde los criterios de aceptación junto con el código, en pasos pequeños.
Los defectos de esta versión los encontraron los casos manuales y el análisis estático, por eso
cada uno se documenta con su primera ejecución fallida, su análisis y su nueva ejecución.

Para reproducirlas:

```powershell
.venv\Scripts\python -m pytest --cov --junitxml=reporte-pytest.xml
```

## Casos manuales

Los casos manuales se ejecutan con un script de Playwright que recorre la aplicación y mide la
interfaz ([`docs/scripts/capturas_y_casos_manuales.py`](../scripts/capturas_y_casos_manuales.py)),
con comandos de Docker y con SonarQube. Después se revisan las capturas. Todos corren contra la
imagen Docker real, en un contenedor con una base de datos limpia.

| Caso | Verifica | Ejecución 1 | Ejecución final | Defecto |
|---|---|---|---|---|
| [CT-M01](#ct-m01) | CA-03.3, RNF-02, RNF-06 | ❌ Fallido | ✅ Aprobado (ejecución 2) | [DEF-04](defectos.md#def-04) |
| [CT-M02](#ct-m02) | CA-08.1, CA-10.2, RNF-06 | ❌ Fallido | ✅ Aprobado (ejecución 2) | [DEF-02](defectos.md#def-02), [DEF-03](defectos.md#def-03) |
| [CT-M03](#ct-m03) | RNF-03, RNF-07 | ❌ Fallido | ✅ Aprobado (ejecución 2) | [DEF-01](defectos.md#def-01) |
| [CT-M04](#ct-m04) | RNF-01 | ✅ Aprobado | ✅ Aprobado | — |
| [CT-M05](#ct-m05) | CA-08.3 | ✅ Aprobado | ✅ Aprobado | — |
| [CT-M06](#ct-m06) | RNF-04 | ❌ Fallido (análisis v2) | ✅ Aprobado (análisis v3) | [Reporte de análisis](../05-analisis-estatico/README.md#54-hallazgo-el-segundo-análisis-rechazó-el-quality-gate) |

### CT-M01

**Revisión del cliente en el celular.**

| Campo | Detalle |
|---|---|
| Precondiciones | Contenedor con base limpia; viewports de 390 × 844 y 360 × 740 px |
| Pasos | 1. Abrir el menú sin sesión. 2. Registrarse. 3. Agregar 1 bolón, 2 empanadas y 1 café. 4. Revisar y confirmar. 5. Abrir «Mis pedidos». En cada pantalla a 360 px, medir el desplazamiento horizontal y el alto de cada control interactivo |
| Esperado | Total en vivo $4,10 tras los 4 artículos; sin desplazamiento horizontal; todos los controles ≥ 44 px (RNF-02); estados con texto, ícono y color (RNF-06) |
| Ejecución 1 (24-11, imagen `9407d61`) | **Fallido.** Total en vivo $4,10 y sin desplazamiento horizontal, pero había controles de 20 a 36 px: enlaces y botón de la barra 20 px, «Registrarme» 36 px, campos de cantidad 24 px, «Ver productos» 34 px. → DEF-04. [Resultados medidos](evidencias/casos-manuales-ejecucion-1.json) |
| Ejecución 2 (24-11, imagen con el PR #25) | **Aprobado.** 5 pantallas sin desplazamiento horizontal; 47 controles, el menor de 44 px. [Resultados medidos](evidencias/casos-manuales.json) |

Durante la ejecución 2 también se corrigió el propio script de medición. Medía justo después de
enviar un formulario, antes de que la página nueva cargara su hoja de estilos, y reportaba
falsamente botones de 17 px. Ahora espera la carga completa (`wait_for_load_state("load")`). Este
falso positivo no se contó como defecto del producto.

### CT-M02

**Revisión del tablero del personal.**

| Campo | Detalle |
|---|---|
| Precondiciones | Pedidos en los tres estados; viewport de 1280 × 860 px |
| Pasos | 1. Ingresar como personal. 2. Avanzar pedidos hasta tener las tres columnas. 3. Escribir un código incorrecto en un pedido Listo. 4. Escribir el código correcto en minúsculas y sin guion |
| Esperado | Resumen con concordancia de número («3 pendientes», «1 listo para retirar»); el aviso de error identifica el pedido; la entrega se registra |
| Ejecución 1 (24-11, rama `feature/web-personal`) | **Fallido.** Resumen «2 pendiente» y «2 listo para retirar» → DEF-02. Aviso «No se registró la entrega. El código no coincide con este pedido», sin decir cuál → DEF-03. [Captura del tablero](evidencias/ct-m02-ejecucion-1-tablero.png) · [captura del aviso](evidencias/ct-m02-ejecucion-1-aviso.png) |
| Ejecución 2 (24-11, `v1.0.0`) | **Aprobado.** «3 pendientes · 1 en preparación · 1 listo para retirar · 0 entregados hoy». Aviso: «Pedido WSX-3T3: no se registró la entrega. El código no coincide con este pedido…». Entrega con `wsx3t3` registrada. [Resultados](evidencias/casos-manuales.json) |

### CT-M03

**Instalación y salud del contenedor.**

| Campo | Detalle |
|---|---|
| Pasos | 1. `docker compose up -d --build` con un `.env`. 2. Esperar `healthy`. 3. Consultar la política de reinicio, los límites, el usuario y el volumen. 4. Pedir `/health`, `/`, `/personal/ingresar`, `/docs`, la hoja de estilos y una fuente |
| Esperado | Contenedor `healthy`, `unless-stopped`, 256 MB, 0,5 CPU, usuario sin privilegios, volumen `cafeteria-data`; todas las respuestas 200 con su tipo correcto |
| Ejecución 1 (24-11, `7062db0`) | **Fallido.** Todo correcto salvo `GET /static/fonts/jetbrains-mono.woff2 → 200 application/octet-stream` → DEF-01 |
| Ejecución 2 (24-11, `v1.0.0`) | **Aprobado.** `healthy`, `unless-stopped`, 268435456 bytes, 500000000 nanoCPU, usuario `cafeteria`; fuente `200 font/woff2`. [Salida completa](evidencias/ct-m03-contenedor.txt) |

### CT-M04

**Persistencia en el volumen de Docker.**

| Campo | Detalle |
|---|---|
| Pasos | 1. Con datos creados (CT-M01 y CT-M02), contar las filas de cada tabla. 2. `docker rm -f` del contenedor. 3. Crear un contenedor nuevo con el mismo volumen. 4. Contar de nuevo |
| Esperado | Mismos productos, clientes, pedidos, detalles y estados |
| Ejecución 1 (24-11, `v1.0.0`) | **Aprobado.** Antes y después: 10 productos, 2 clientes, 5 pedidos, 10 detalles, con los mismos códigos y estados. [Salida](evidencias/ct-m04-persistencia.txt) |

### CT-M05

**Recarga del tablero sin perder lo escrito.**

| Campo | Detalle |
|---|---|
| Pasos | 1. Abrir el tablero con un pedido Listo y marcar la página con una variable de JavaScript. 2. Escribir «K7P» en el código y esperar 25 s. 3. Borrar el texto, quitar el foco y esperar 25 s |
| Esperado | En el paso 2 la página no se recarga y el texto se conserva; en el paso 3 la página se recarga |
| Ejecución 1 (24-11, `v1.0.0`) | **Aprobado.** `conserva_lo_escrito_tras_25s: true`, `recarga_sin_escritura_tras_25s: true`. [Resultados](evidencias/casos-manuales.json) |

### CT-M06

**Análisis estático y cobertura.**

| Campo | Detalle |
|---|---|
| Pasos | Ruff y el análisis de SonarQube con el perfil *Sonar way comprehensive* y la cobertura de pytest |
| Esperado | Ruff sin observaciones, Quality Gate aprobado y cobertura ≥ 80 % (RNF-04) |
| Ejecución 1 (análisis v1) | Quality Gate aprobado, pero con 13 problemas y confiabilidad C. Se corrigieron |
| Ejecución 2 (análisis v2) | **Fallido.** Quality Gate rechazado: cobertura del código nuevo 75,9 % |
| Ejecución 3 (análisis v3, `v1.0.0`) | **Aprobado.** 0 problemas, A en las tres cualidades, cobertura 97,2 %. [Reporte](../05-analisis-estatico/README.md) |

## Auditoría de configuración del Release 1.0

Antes de etiquetar `v1.0.0` se comprobó (semana 7 [6]):

- [x] Los 37 criterios de aceptación tienen al menos un caso de prueba aprobado ([matriz](../01-requisitos/matriz-trazabilidad.md)).
- [x] Las 7 reglas de negocio y los 7 requisitos no funcionales tienen verificación aprobada.
- [x] No hay defectos abiertos: DEF-01 a DEF-04 están cerrados y sus casos se volvieron a ejecutar.
- [x] Quality Gate aprobado y CI en verde sobre el commit etiquetado.
- [x] Los manuales y las capturas corresponden a la imagen construida desde `v1.0.0`.
- [x] `CHANGELOG.md` describe la versión y la Release de GitHub publica sus notas.
