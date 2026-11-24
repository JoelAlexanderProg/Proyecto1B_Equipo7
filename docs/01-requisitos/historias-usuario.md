# Historias de usuario

Derivadas de la especificación del cliente v1.0. Cada historia tiene criterios de aceptación verificables con el formato *Dado / Cuando / Entonces*; el criterio `CA-XX.Y` se verifica con el caso de prueba `CT-XX.Y` ([catálogo](../06-pruebas/casos-de-prueba.md)).

| HU | Rol | Título | Origen | Issue | PR |
|---|---|---|---|---|---|
| [HU-01](#hu-01) | Cliente | Consultar el menú | RU-01 · RN-02 · RN-NEG-02 | [#7](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/7) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2) |
| [HU-02](#hu-02) | Cliente | Armar el pedido | RU-02 · RN-NEG-01 · RN-NEG-02 · A7 | [#8](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/8) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2) |
| [HU-03](#hu-03) | Cliente | Conocer el total antes de confirmar | RU-03 · RN-NEG-03 | [#9](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/9) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2) |
| [HU-04](#hu-04) | Cliente | Confirmar el pedido y recibir el código de retiro | RU-04 · RN-NEG-04 · RN-NEG-05 · RN-NEG-06 · PN-01 | [#10](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/10) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2) |
| [HU-05](#hu-05) | Cliente | Consultar el estado de mis pedidos | RU-05 · RN-03 | [#11](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/11) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2) |
| [HU-06](#hu-06) | Cliente | Registrarme e ingresar | Dominio «Cliente» §7 · A1 · A2 | [#12](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/12) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2) |
| [HU-07](#hu-07) | Personal | Mantener el menú | RU-06 · RN-NEG-04 · A5 · A6 | [#13](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/13) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3) |
| [HU-08](#hu-08) | Personal | Ver los pedidos por estado | RU-07 · RN-01 · RN-03 · PN-02 | [#14](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/14) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3) |
| [HU-09](#hu-09) | Personal | Registrar el avance de un pedido | RU-07 · RN-NEG-06 | [#15](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/15) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3) |
| [HU-10](#hu-10) | Personal | Entregar el pedido verificando el código | RU-07 · RN-04 · RN-NEG-07 · PN-02 | [#16](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/16) | [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3) |
| [HU-11](#hu-11) | Personal | Ingresar como personal | A4 · RNF-05 | [#17](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/17) | [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3) |

## HU-01

**Consultar el menú.** Como cliente, quiero consultar el menú con los productos disponibles y sus precios, para decidir qué pedir.

Origen: RU-01 · RN-02 · RN-NEG-02 · Issue [#7](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/7) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2)

Requisitos funcionales derivados: [RF-01](requisitos-funcionales.md#rf-01), [RF-02](requisitos-funcionales.md#rf-02), [RF-03](requisitos-funcionales.md#rf-03)

- **CA-01.1.** **Dado** un menú con productos registrados, **cuando** cualquier persona abre la página principal, **entonces** ve cada producto con su nombre y su precio, agrupados en Alimentos y Bebidas.
- **CA-01.2.** **Dado** un producto marcado como no disponible, **cuando** se muestra el menú, **entonces** aparece como «No disponible» y no se puede agregar al pedido.
- **CA-01.3.** **Dado** el servicio en ejecución, **cuando** se consulta `GET /api/v1/productos?disponibles=true`, **entonces** la respuesta solo incluye productos disponibles, con el precio en dólares y dos decimales.

## HU-02

**Armar el pedido.** Como cliente, quiero elegir productos y cantidades, para armar mi pedido.

Origen: RU-02 · RN-NEG-01 · RN-NEG-02 · A7 · Issue [#8](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/8) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2)

Requisitos funcionales derivados: [RF-04](requisitos-funcionales.md#rf-04), [RF-05](requisitos-funcionales.md#rf-05), [RF-06](requisitos-funcionales.md#rf-06)

- **CA-02.1.** **Dado** un cliente identificado, **cuando** pide revisar sin elegir productos, **entonces** ve «El pedido debe incluir al menos un producto» y no avanza.
- **CA-02.2.** **Dado** un cliente identificado, **cuando** escribe una cantidad que no es un entero entre 1 y 20, **entonces** ve el motivo y no avanza; 1 y 20 se aceptan.
- **CA-02.3.** **Dado** un producto no disponible, **cuando** se intenta incluirlo en un pedido, **entonces** se informa que no está disponible y el pedido no avanza.
- **CA-02.4.** **Dado** un visitante sin sesión, **cuando** intenta revisar un pedido, **entonces** se le lleva a la página de ingreso.

## HU-03

**Conocer el total antes de confirmar.** Como cliente, quiero ver el importe total mientras armo el pedido, para saber cuánto pagaré antes de confirmar.

Origen: RU-03 · RN-NEG-03 · Issue [#9](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/9) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2)

Requisitos funcionales derivados: [RF-07](requisitos-funcionales.md#rf-07), [RF-08](requisitos-funcionales.md#rf-08)

- **CA-03.1.** **Dado** una selección válida, **cuando** el cliente revisa el pedido, **entonces** ve cada línea con su subtotal y un total igual a la suma de precio × cantidad.
- **CA-03.2.** **Dado** un pedido en revisión, **cuando** cambia el precio de un producto antes de confirmar, **entonces** se muestra el nuevo total y el pedido no se confirma hasta que el cliente lo vea.
- **CA-03.3.** **Dado** el menú abierto en el celular, **cuando** el cliente cambia una cantidad, **entonces** la barra inferior actualiza al instante los artículos y el total.

## HU-04

**Confirmar el pedido y recibir el código de retiro.** Como cliente, quiero confirmar mi pedido y recibir un código de retiro, para identificarlo al retirarlo.

Origen: RU-04 · RN-NEG-04 · RN-NEG-05 · RN-NEG-06 · PN-01 · Issue [#10](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/10) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2)

Requisitos funcionales derivados: [RF-09](requisitos-funcionales.md#rf-09), [RF-10](requisitos-funcionales.md#rf-10), [RF-11](requisitos-funcionales.md#rf-11)

- **CA-04.1.** **Dado** un pedido revisado, **cuando** el cliente lo confirma, **entonces** queda registrado en estado Pendiente con la fecha de registro y un código `XXX-XXX` sin los caracteres 0, O, 1, I ni L.
- **CA-04.2.** **Dado** que el código generado ya existe, **cuando** se confirma el pedido, **entonces** el sistema genera otro y ningún par de pedidos comparte código.
- **CA-04.3.** **Dado** un pedido confirmado, **cuando** el personal cambia el precio de uno de sus productos, **entonces** el pedido conserva el precio y el total con que se confirmó.
- **CA-04.4.** **Dado** un pedido en revisión, **cuando** uno de sus productos deja de estar disponible antes de confirmar, **entonces** se informa el motivo y el pedido no se confirma (PN-01, paso 7).

## HU-05

**Consultar el estado de mis pedidos.** Como cliente, quiero consultar el estado de mis pedidos, para saber cuándo retirarlos.

Origen: RU-05 · RN-03 · Issue [#11](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/11) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2)

Requisitos funcionales derivados: [RF-12](requisitos-funcionales.md#rf-12), [RF-13](requisitos-funcionales.md#rf-13), [RF-14](requisitos-funcionales.md#rf-14)

- **CA-05.1.** **Dado** un pedido confirmado, **cuando** el cliente abre su detalle, **entonces** ve el código de retiro, el estado vigente y la hora de cada etapa alcanzada.
- **CA-05.2.** **Dado** un cliente con pedidos, **cuando** abre «Mis pedidos», **entonces** ve sus pedidos del más reciente al más antiguo con su estado.
- **CA-05.3.** **Dado** dos clientes, **cuando** uno intenta abrir el pedido del otro, **entonces** recibe «No encontramos esa página».

## HU-06

**Registrarme e ingresar.** Como cliente, quiero registrarme con mis datos institucionales, para que mis pedidos queden asociados a mí.

Origen: Dominio «Cliente» §7 · A1 · A2 · Issue [#12](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/12) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#2](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/2)

Requisitos funcionales derivados: [RF-15](requisitos-funcionales.md#rf-15), [RF-16](requisitos-funcionales.md#rf-16), [RF-17](requisitos-funcionales.md#rf-17), [RF-18](requisitos-funcionales.md#rf-18)

- **CA-06.1.** **Dado** datos válidos, **cuando** el cliente se registra, **entonces** recibe un código de cliente `CLI-0001` y su sesión queda iniciada.
- **CA-06.2.** **Dado** una cédula con dígito verificador incorrecto, un celular que no empieza con 09 o un correo de otro dominio, **cuando** se registra, **entonces** ve el motivo y no se crea la cuenta.
- **CA-06.3.** **Dado** un cliente registrado, **cuando** otra persona intenta registrarse con la misma cédula o el mismo correo, **entonces** se rechaza el registro.
- **CA-06.4.** **Dado** un cliente registrado, **cuando** ingresa con su correo y su cédula, **entonces** inicia sesión; si no coinciden, ve un mensaje y no ingresa. Al salir, la sesión se cierra.

## HU-07

**Mantener el menú.** Como personal, quiero registrar y actualizar productos, precios y disponibilidad, para mantener el menú al día.

Origen: RU-06 · RN-NEG-04 · A5 · A6 · Issue [#13](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/13) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3)

Requisitos funcionales derivados: [RF-19](requisitos-funcionales.md#rf-19), [RF-20](requisitos-funcionales.md#rf-20), [RF-21](requisitos-funcionales.md#rf-21)

- **CA-07.1.** **Dado** el personal en la sección Menú, **cuando** agrega un producto válido, **entonces** el sistema le asigna el siguiente código de su categoría (`ALI-006`, `BEB-006`).
- **CA-07.2.** **Dado** un precio vacío, negativo, con más de dos decimales o mayor que $100, **cuando** se guarda el producto, **entonces** se muestra el motivo y no se guarda.
- **CA-07.3.** **Dado** pedidos confirmados, **cuando** el personal edita el precio de un producto, **entonces** el menú muestra el precio nuevo y los pedidos conservan el anterior.
- **CA-07.4.** **Dado** un producto, **cuando** el personal lo marca no disponible o disponible, **entonces** el menú del cliente lo refleja de inmediato.

## HU-08

**Ver los pedidos por estado.** Como personal, quiero ver los pedidos agrupados por estado, para atender primero los pendientes.

Origen: RU-07 · RN-01 · RN-03 · PN-02 · Issue [#14](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/14) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3)

Requisitos funcionales derivados: [RF-22](requisitos-funcionales.md#rf-22), [RF-23](requisitos-funcionales.md#rf-23)

- **CA-08.1.** **Dado** pedidos en curso, **cuando** el personal abre el tablero, **entonces** los ve en tres columnas (Pendiente, En preparación, Listo para retirar) con sus conteos y los entregados del día.
- **CA-08.2.** **Dado** varios pedidos en una columna, **cuando** se muestra el tablero, **entonces** aparecen del más antiguo al más reciente.
- **CA-08.3.** **Dado** el tablero abierto, **cuando** pasan 20 segundos, **entonces** se recarga, salvo que el personal esté escribiendo un código.

## HU-09

**Registrar el avance de un pedido.** Como personal, quiero registrar el avance de un pedido, para que el cliente conozca su estado.

Origen: RU-07 · RN-NEG-06 · Issue [#15](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/15) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3)

Requisitos funcionales derivados: [RF-24](requisitos-funcionales.md#rf-24), [RF-25](requisitos-funcionales.md#rf-25)

- **CA-09.1.** **Dado** un pedido Pendiente, **cuando** el personal registra el avance dos veces, **entonces** pasa a En preparación y luego a Listo para retirar, con la hora de cada cambio.
- **CA-09.2.** **Dado** un pedido Listo para retirar o Entregado, **cuando** se intenta avanzarlo sin código, **entonces** se rechaza y el estado no cambia.
- **CA-09.3.** **Dado** dos personas que cambian a la vez el estado del mismo pedido, **cuando** la segunda guarda, **entonces** se le avisa que el pedido cambió y su cambio no se aplica.

## HU-10

**Entregar el pedido verificando el código.** Como personal, quiero entregar un pedido solo si el código coincide, para no entregar pedidos equivocados.

Origen: RU-07 · RN-04 · RN-NEG-07 · PN-02 · Issue [#16](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/16) · Implementación: [#1](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/1), [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3)

Requisitos funcionales derivados: [RF-26](requisitos-funcionales.md#rf-26), [RF-27](requisitos-funcionales.md#rf-27)

- **CA-10.1.** **Dado** un pedido Listo para retirar, **cuando** el personal escribe el código que presenta el cliente (sin importar mayúsculas, espacios o guion), **entonces** el pedido pasa a Entregado.
- **CA-10.2.** **Dado** un pedido Listo para retirar, **cuando** el código no coincide, **entonces** no se entrega, sigue Listo y el aviso identifica el pedido.
- **CA-10.3.** **Dado** un pedido Pendiente o En preparación, **cuando** se intenta entregarlo, **entonces** se rechaza.

## HU-11

**Ingresar como personal.** Como personal, quiero ingresar con una cuenta, para que solo el personal cambie el menú y los estados.

Origen: A4 · RNF-05 · Issue [#17](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/issues/17) · Implementación: [#3](https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/pull/3)

Requisitos funcionales derivados: [RF-28](requisitos-funcionales.md#rf-28), [RF-29](requisitos-funcionales.md#rf-29)

- **CA-11.1.** **Dado** la cuenta del personal, **cuando** ingresa con el usuario y la clave correctos, **entonces** ve el tablero; con datos incorrectos ve «Usuario o clave incorrectos».
- **CA-11.2.** **Dado** un visitante o un cliente, **cuando** abre `/personal` o `/personal/menu`, **entonces** se le lleva al ingreso del personal. Al salir, la sesión del personal se cierra.
- **CA-11.3.** **Dado** el arranque de la aplicación, **cuando** falta la clave del personal o tiene menos de 8 caracteres, **entonces** la aplicación no arranca e indica cómo configurarla.
