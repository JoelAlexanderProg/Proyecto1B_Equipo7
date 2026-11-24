# 1. Documentación de requisitos

Fuente: especificación del cliente v1.0 (27-10-2026), «Gestión de pedidos de una cafetería
universitaria». Este documento la convierte en requisitos verificables: historias de usuario con
criterios de aceptación, requisitos no funcionales medibles y las aclaraciones que la
especificación pide resolver antes de implementar (§10).

- [Historias de usuario y criterios de aceptación](historias-usuario.md) (11 HU, 37 criterios)
- [Matriz de trazabilidad](matriz-trazabilidad.md): requisito → HU → Issue → caso de prueba → código → PR

## 1.1 Alcance del Release 1.0

**Incluye:** consulta del menú, registro de pedidos anticipados con total y código de retiro,
seguimiento del estado, atención del pedido por el personal hasta la entrega con verificación del
código, y mantenimiento del menú. La información persiste entre ejecuciones.

**No incluye** (especificación §8): pago electrónico o cobro en línea; notificaciones por correo o
mensajería; impresoras o lectores de códigos (el código se muestra en pantalla); promociones,
reembolsos, pedidos programados e inventario de ingredientes. Gestionar las expectativas del
cliente con un alcance explícito es el primer principio de despliegue de Pressman [1].

## 1.2 Actores

| Actor | Descripción | Acceso |
|---|---|---|
| Cliente | Estudiante o docente que consulta el menú, pide y retira | Registro con datos institucionales; ingreso con correo y cédula |
| Personal de cafetería | Mantiene el menú y procesa los pedidos | Cuenta única configurada por variables de entorno |

## 1.3 Reglas de negocio

Las siete reglas se implementan en la capa de dominio, sin depender de la interfaz ni de la base de
datos ([diseño](../02-diseno/README.md)). La matriz indica la función exacta y sus pruebas.

| Regla | Enunciado | Cómo se garantiza |
|---|---|---|
| RN-NEG-01 | Al menos un producto; cantidades enteras positivas | `construir_detalles` y `validar_cantidad` rechazan selecciones vacías, no enteras, menores que 1 o mayores que 20 |
| RN-NEG-02 | Solo productos disponibles en nuevos pedidos | `ProductoNoDisponible` al revisar y otra vez al confirmar |
| RN-NEG-03 | Total = Σ precio vigente × cantidad | `calcular_total` con `Decimal`; el total es una consulta, no un dato guardado |
| RN-NEG-04 | El precio del pedido no cambia si cambia el menú | `DetallePedido` es inmutable y guarda su propio precio |
| RN-NEG-05 | Código de retiro único | Generador criptográfico + restricción `UNIQUE` + reintento |
| RN-NEG-06 | Pendiente → En preparación → Listo para retirar → Entregado | Tabla de transiciones; saltos y retrocesos lanzan `TransicionNoPermitida` |
| RN-NEG-07 | Entregado solo desde Listo y con el código | `Pedido.entregar` compara el código normalizado |

## 1.4 Requisitos no funcionales

| ID | Requisito | Criterio verificable |
|---|---|---|
| RNF-01 | Persistencia | Productos, clientes y pedidos se conservan al reiniciar la aplicación o recrear el contenedor |
| RNF-02 | Uso desde el celular | Sin desplazamiento horizontal desde 360 px; objetivos táctiles de al menos 44 px |
| RNF-03 | Instalación con un comando | `docker compose up -d --build` con un archivo `.env` |
| RNF-04 | Calidad del código | Ruff sin observaciones, Quality Gate de SonarQube aprobado y cobertura ≥ 80 % |
| RNF-05 | Credenciales fuera del código | Clave del personal y secreto de sesión por variables de entorno; `.env` no se versiona |
| RNF-06 | Estados reconocibles | Texto, ícono y color en cada estado; contraste ≥ 4,5:1 (WCAG 2.1 AA [16]) |
| RNF-07 | Disponibilidad observable | `GET /health` responde `{"estado": "ok"}` y el contenedor reporta su salud a Docker |

## 1.5 Supuestos y aclaraciones

La especificación pide aclarar las ambigüedades antes de implementar (§10). El equipo propuso estos
supuestos el 24-11-2026; A1, A7 y A8 se discutieron y confirmaron explícitamente.

| ID | Tema | Decisión | Estado |
|---|---|---|---|
| A1 | Identificación del cliente | Registro con nombre, apellido, cédula, celular y correo institucional; el sistema asigna `CLI-0001`. Ingreso con correo y cédula, **sin contraseña** en el Release 1.0 | Confirmado |
| A2 | Validación de datos | Cédula ecuatoriana con dígito verificador (módulo 10), celular `09XXXXXXXX`, correo del dominio institucional (configurable, `epn.edu.ec`) | Aplicado |
| A3 | Código de retiro | 6 caracteres de un alfabeto de 31 símbolos sin 0/O ni 1/I/L, formato `XXX-XXX` | Aplicado |
| A4 | Acceso del personal | Una cuenta definida por variables de entorno; sin gestión de usuarios | Aplicado |
| A5 | Productos | No se eliminan, se marcan no disponibles; categoría Alimento o Bebida; código automático `ALI-001`, `BEB-001` | Aplicado |
| A6 | Precio | Dólares, mayor que 0 y hasta $100, dos decimales; `Decimal`, nunca `float` | Aplicado |
| A7 | Cantidad máxima | **20 unidades por producto**: permite pedidos de grupo sin que una sola persona sature la cocina | Confirmado |
| A8 | Cancelación | **No hay cancelación** ni retroceso de estados: RN-NEG-06 solo define el avance | Confirmado |
| A9 | Disponibilidad posterior | Un producto que deja de estar disponible no afecta pedidos ya confirmados | Aplicado |
| A10 | Carrito | La selección no se guarda hasta confirmar; un *pedido* existe solo cuando se confirma (glosario) | Aplicado |
| A11 | Hora | Fecha de registro en hora de Ecuador (UTC−05:00, sin horario de verano) | Aplicado |

## 1.6 Glosario

| Término | Definición |
|---|---|
| Menú | Conjunto de productos que la cafetería ofrece |
| Producto disponible | Producto habilitado para incorporarse a nuevos pedidos |
| Pedido confirmado | Solicitud registrada con un código de retiro y estado Pendiente |
| Código de retiro | Identificador único (`XXX-XXX`) que permite localizar y entregar un pedido |
| Estado de pedido | Etapa de atención: Pendiente, En preparación, Listo para retirar o Entregado |
| Detalle del pedido | Producto incluido en un pedido, con su cantidad y el precio considerado |

## 1.7 Fundamento

- Historias, criterios de aceptación verificables y evidencia trazable (Issue, caso de prueba y PR)
  siguen el ejemplo HU-07 de la semana 5 [6].
- Los criterios cumplen las características de un buen requisito de ISO/IEC/IEEE 29148 [7]:
  necesarios, sin ambigüedad, verificables y trazables.
- La matriz de trazabilidad permite rastrear un requisito hacia arriba y hacia abajo y analizar el
  impacto de un cambio (semana 7 [6], León [4]). Todas las pruebas son trazables a requisitos del
  cliente, primer principio de prueba de Davis [1].
