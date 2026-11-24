# Defectos y base de conocimiento

Cada defecto se registró como Issue con la plantilla de reporte de problema. Su análisis usa la
terminología de IEEE 610 [5] (semana 6 [6]):
- **Error:** la acción humana que produjo un resultado incorrecto.
- **Defecto:** la imperfección que quedó en el producto.
- **Fallo:** lo que se observó al ejecutar.

La severidad y la fase de origen siguen las clasificaciones de la semana 7.

| Defecto | Issue | Severidad | Fase de origen | Caso que lo detectó | Corrección | Estado |
|---|---|---|---|---|---|---|
| [DEF-01](#def-01) | [#18](../../../../issues/18) | No fatal | Codificación | CT-M03 | [PR #4](../../../../pull/4) | Cerrado |
| [DEF-02](#def-02) | [#19](../../../../issues/19) | Cosmético | Codificación | CT-M02 | [PR #3](../../../../pull/3) | Cerrado |
| [DEF-03](#def-03) | [#20](../../../../issues/20) | Cosmético | Diseño | CT-M02 | [PR #3](../../../../pull/3) | Cerrado |
| [DEF-04](#def-04) | [#24](../../../../issues/24) | No fatal | Diseño | CT-M01 | [PR #25](../../../../pull/25) | Cerrado |

## DEF-01

**Las fuentes WOFF2 se sirven como `application/octet-stream` en el contenedor.**

| Campo | Detalle |
|---|---|
| Reproducción | `docker compose up -d --build` y luego `curl -s -o /dev/null -w "%{content_type}" http://127.0.0.1:8000/static/fonts/inter.woff2` |
| Esperado | `font/woff2` |
| Obtenido | `application/octet-stream` |
| Fallo | El servidor declara un tipo genérico para las fuentes. Los navegadores las cargan igual, pero un proxy o la cabecera `X-Content-Type-Options: nosniff` podrían bloquearlas |
| Defecto | `StaticFiles` deduce el tipo con el módulo `mimetypes` de Python, que depende de la tabla de tipos del sistema operativo. La imagen `python:3.12-slim` no trae `/etc/mime.types` |
| Error | Se dio por hecho que el entorno de ejecución tendría la misma configuración que el de desarrollo: el caso «en mi máquina funciona» de la semana 2 |
| Solución | `mimetypes.add_type("font/woff2", ".woff2")` en `web.py`, más la prueba de sistema `test_fuentes_se_sirven_con_su_tipo` |
| Nueva ejecución | CT-M03, ejecución 2: `200 font/woff2`. La prueba nueva queda en la regresión |

## DEF-02

**El resumen del tablero no concuerda en número.**

| Campo | Detalle |
|---|---|
| Reproducción | Confirmar dos pedidos y abrir `/personal` |
| Esperado | «2 pendientes», «2 listos para retirar», «1 entregado hoy» |
| Obtenido | «2 pendiente», «2 listo para retirar» ([captura](evidencias/ct-m02-ejecucion-1-tablero.png)) |
| Defecto | La plantilla usaba la etiqueta del estado, en singular, para cualquier cantidad |
| Error | Se reutilizó la etiqueta del dominio, pensada para un pedido, como texto de un conteo |
| Solución | Tabla de nombres en singular y plural en `tablero.html`; la prueba del flujo verifica «1 entregado hoy» |
| Nueva ejecución | CT-M02, ejecución 2: «3 pendientes · 1 en preparación · 1 listo para retirar» |

## DEF-03

**El aviso de código incorrecto no identifica el pedido.**

| Campo | Detalle |
|---|---|
| Reproducción | Llevar un pedido a Listo y escribir un código distinto en su tarjeta |
| Esperado | Un aviso que diga qué pedido no se entregó |
| Obtenido | «No se registró la entrega. El código no coincide con este pedido…» ([captura](evidencias/ct-m02-ejecucion-1-aviso.png)) |
| Defecto | El aviso aparece arriba del tablero, lejos de la tarjeta, y el mensaje del dominio no conoce el código del pedido |
| Error | El mensaje se diseñó desde el dominio («este pedido») sin pensar dónde lo lee el personal |
| Solución | La ruta antepone «Pedido XXX-XXX:» al mensaje; la prueba del flujo lo verifica |
| Nueva ejecución | CT-M02, ejecución 2: «Pedido WSX-3T3: no se registró la entrega…» |

## DEF-04

**Controles del cliente con menos de 44 px de alto.**

| Campo | Detalle |
|---|---|
| Reproducción | Viewport de 360 × 740 px; medir el alto de cada control interactivo (CT-M01) |
| Esperado | Todos ≥ 44 px (RNF-02) |
| Obtenido | Barra 20 px, «Registrarme» 36 px, campos de cantidad 24 px, «Ver productos» 34 px, «Seguir agregando» 22 px |
| Fallo | En el celular, los enlaces de la barra y los campos de cantidad son difíciles de tocar con precisión |
| Defecto | La hoja de estilos fijaba 44 px en los botones principales, pero no en los enlaces de la barra, la variante `boton-chico`, los campos de cantidad ni el resumen desplegable |
| Error | En la primera revisión visual el requisito se verificó «a ojo», sin medir |
| Solución | `min-height: 44px` en esos elementos (PR #25) |
| Nueva ejecución | CT-M01, ejecución 2: 47 controles medidos, el menor de 44 px. Regresión completa: 113 pruebas aprobadas |

## Hallazgo al probar el manual de instalación

Antes de publicar el manual se ejecutó cada comando. Pressman recuerda que la mayoría de los
defectos se originan en la documentación y que probarla tiene valor (principio 7 [1]).

| Campo | Detalle |
|---|---|
| Procedimiento probado | Restaurar un respaldo con `docker compose stop`, `docker cp respaldo.db cafepoli:/app/data/cafeteria.db` y `docker compose start` |
| Esperado | Los datos del respaldo en la base y la aplicación funcionando |
| Obtenido | Los datos se restauraron (5 pedidos, integridad `ok`), pero la escritura falló: «attempt to write a readonly database» |
| Causa | `docker cp` deja el archivo como propiedad de `root`; la aplicación corre como el usuario sin privilegios `cafeteria` |
| Solución | El manual restaura con la API de respaldo de SQLite desde dentro del contenedor, escribiendo sobre el archivo existente, que conserva su propietario. Se agregó el síntoma a la tabla de solución de problemas |
| Nueva ejecución | Pedidos borrados → restauración → 5 pedidos, propietario `cafeteria`, escritura correcta, integridad `ok`, sin detener el servicio |

Como el defecto estaba en un procedimiento todavía no publicado, se corrigió en el mismo documento
y no se abrió una Issue.

## Análisis causal y prevención

La semana 7 propone analizar las causas para que los defectos no se repitan:

| Causa (semana 7) | Defectos | Acción preventiva |
|---|---|---|
| Diferencias entre el entorno de desarrollo y el de ejecución | DEF-01 | La CI construye la imagen en cada PR y CT-M03 se ejecuta contra la imagen real |
| Requisitos no funcionales sin un procedimiento de medición | DEF-04 | CT-M01 mide con un script en lugar de revisar a ojo |
| Textos de la interfaz escritos desde el código y no desde el usuario | DEF-02, DEF-03 | La revisión visual (CT-M02) forma parte de la definición de terminado de las pantallas |
| Supervisión del proceso (incidente [INC-01](../03-ambiente-desarrollo/flujo-de-trabajo.md#310-incidente-inc-01)) | — | Rama `main` protegida y *auto-merge* que espera la CI |

## Base de conocimiento de defectos

La semana 7 propone una base de conocimiento que se pueda buscar por categoría, fase, causa y
severidad. Las Issues con la etiqueta [`defecto`](../../../../issues?q=label%3Adefecto) cumplen
ese papel: cada una tiene sus campos y se puede filtrar en GitHub.

| Lección | Aplicar cuando |
|---|---|
| Registrar explícitamente los tipos MIME que sirve la aplicación | Se sirven archivos estáticos desde una imagen *slim* |
| Medir el tamaño de los objetivos táctiles en el viewport más pequeño soportado | Se crea o se modifica una pantalla del cliente |
| Escribir los textos de conteo con concordancia de número | Se muestra «N elementos» en la interfaz |
| Los avisos globales deben nombrar el objeto al que se refieren | Un mensaje se muestra lejos del elemento que lo causó |
| Esperar la carga completa antes de medir en Playwright | Se automatiza una medición después de enviar un formulario |
