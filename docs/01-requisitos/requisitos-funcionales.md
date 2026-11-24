# Requisitos funcionales

Expresan como obligaciones del sistema lo que exigen las [historias de usuario](historias-usuario.md). Cada requisito funcional (RF) sale de los criterios de aceptación de una historia y se verifica con los casos de prueba de esos criterios (`CA-XX.Y` → `CT-XX.Y`, [catálogo](../06-pruebas/casos-de-prueba.md)). Los 29 RF cubren los 37 criterios: ninguno queda sin un requisito que lo exprese.

Se redactan como enunciados «El sistema debe…», cada uno con una sola capacidad verificable, siguiendo las características de un buen requisito de ISO/IEC/IEEE 29148: necesario, sin ambigüedad, verificable y trazable.

## HU-01 · Consultar el menú

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-01"></a>**RF-01** | El sistema debe mostrar el menú sin exigir una cuenta, con el nombre y el precio de cada producto, agrupados en Alimentos y Bebidas. | [CA-01.1](historias-usuario.md#hu-01) | CT-01.1 |
| <a id="rf-02"></a>**RF-02** | El sistema debe mostrar como «No disponible» cada producto no disponible e impedir que se incluya en un pedido. | [CA-01.2](historias-usuario.md#hu-01), [CA-02.3](historias-usuario.md#hu-02) | CT-01.2, CT-02.3 |
| <a id="rf-03"></a>**RF-03** | El sistema debe publicar el menú en `GET /api/v1/productos`, con un filtro de productos disponibles y el precio en dólares con dos decimales. | [CA-01.3](historias-usuario.md#hu-01) | CT-01.3 |

## HU-02 · Armar el pedido

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-04"></a>**RF-04** | El sistema debe permitir al cliente identificado elegir productos disponibles con cantidades enteras de 1 a 20 por producto. | [CA-02.2](historias-usuario.md#hu-02), [CA-02.3](historias-usuario.md#hu-02) | CT-02.2, CT-02.3 |
| <a id="rf-05"></a>**RF-05** | El sistema debe impedir la revisión de un pedido sin productos o con cantidades no válidas, e informar el motivo. | [CA-02.1](historias-usuario.md#hu-02), [CA-02.2](historias-usuario.md#hu-02) | CT-02.1, CT-02.2 |
| <a id="rf-06"></a>**RF-06** | El sistema debe exigir la sesión del cliente para revisar y confirmar pedidos, y llevar al ingreso a quien no la tenga. | [CA-02.4](historias-usuario.md#hu-02) | CT-02.4 |

## HU-03 · Conocer el total antes de confirmar

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-07"></a>**RF-07** | El sistema debe mostrar el subtotal de cada línea y el total del pedido (Σ precio × cantidad) antes de confirmar, y actualizar el total al cambiar una cantidad. | [CA-03.1](historias-usuario.md#hu-03), [CA-03.3](historias-usuario.md#hu-03) | CT-03.1, CT-03.3 |
| <a id="rf-08"></a>**RF-08** | El sistema debe impedir la confirmación si el total cambió desde que el cliente lo revisó, y mostrarle el total nuevo. | [CA-03.2](historias-usuario.md#hu-03) | CT-03.2 |

## HU-04 · Confirmar el pedido y recibir el código de retiro

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-09"></a>**RF-09** | El sistema debe registrar el pedido confirmado en estado Pendiente, con su fecha de registro y un código de retiro único `XXX-XXX` sin los caracteres 0, O, 1, I ni L. | [CA-04.1](historias-usuario.md#hu-04), [CA-04.2](historias-usuario.md#hu-04) | CT-04.1, CT-04.2 |
| <a id="rf-10"></a>**RF-10** | El sistema debe conservar en cada pedido el precio con que se confirmó cada producto, aunque después cambie el menú. | [CA-04.3](historias-usuario.md#hu-04), [CA-07.3](historias-usuario.md#hu-07) | CT-04.3, CT-07.3 |
| <a id="rf-11"></a>**RF-11** | El sistema debe verificar otra vez la disponibilidad al confirmar y no confirmar el pedido si un producto dejó de estar disponible. | [CA-04.4](historias-usuario.md#hu-04) | CT-04.4 |

## HU-05 · Consultar el estado de mis pedidos

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-12"></a>**RF-12** | El sistema debe mostrar al cliente el detalle de su pedido: código de retiro, estado vigente y hora de cada etapa alcanzada. | [CA-05.1](historias-usuario.md#hu-05) | CT-05.1 |
| <a id="rf-13"></a>**RF-13** | El sistema debe listar los pedidos del cliente, del más reciente al más antiguo, con su estado. | [CA-05.2](historias-usuario.md#hu-05) | CT-05.2 |
| <a id="rf-14"></a>**RF-14** | El sistema debe impedir que un cliente consulte los pedidos de otro. | [CA-05.3](historias-usuario.md#hu-05) | CT-05.3 |

## HU-06 · Registrarme e ingresar

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-15"></a>**RF-15** | El sistema debe registrar clientes con nombre, apellido, cédula, celular y correo institucional, asignarles un código `CLI-0001` e iniciar su sesión. | [CA-06.1](historias-usuario.md#hu-06) | CT-06.1 |
| <a id="rf-16"></a>**RF-16** | El sistema debe validar la cédula con su dígito verificador, el celular (`09` y ocho dígitos) y el dominio del correo, e informar el motivo del rechazo. | [CA-06.2](historias-usuario.md#hu-06) | CT-06.2 |
| <a id="rf-17"></a>**RF-17** | El sistema debe rechazar el registro con una cédula o un correo ya registrados. | [CA-06.3](historias-usuario.md#hu-06) | CT-06.3 |
| <a id="rf-18"></a>**RF-18** | El sistema debe permitir al cliente ingresar con su correo y su cédula, rechazar el ingreso si no coinciden y cerrar la sesión al salir. | [CA-06.4](historias-usuario.md#hu-06) | CT-06.4 |

## HU-07 · Mantener el menú

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-19"></a>**RF-19** | El sistema debe permitir al personal registrar productos con nombre, categoría, precio y disponibilidad, y asignar a cada uno el código siguiente de su categoría. | [CA-07.1](historias-usuario.md#hu-07) | CT-07.1 |
| <a id="rf-20"></a>**RF-20** | El sistema debe rechazar precios vacíos, menores o iguales a 0, mayores que $100 o con más de dos decimales, sin guardar el producto. | [CA-07.2](historias-usuario.md#hu-07) | CT-07.2 |
| <a id="rf-21"></a>**RF-21** | El sistema debe permitir al personal editar productos y cambiar su disponibilidad, con efecto inmediato en el menú del cliente. | [CA-07.3](historias-usuario.md#hu-07), [CA-07.4](historias-usuario.md#hu-07) | CT-07.3, CT-07.4 |

## HU-08 · Ver los pedidos por estado

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-22"></a>**RF-22** | El sistema debe mostrar al personal los pedidos en curso en tres columnas (Pendiente, En preparación y Listo para retirar), del más antiguo al más reciente, con sus conteos y los entregados del día. | [CA-08.1](historias-usuario.md#hu-08), [CA-08.2](historias-usuario.md#hu-08) | CT-08.1, CT-08.2 |
| <a id="rf-23"></a>**RF-23** | El sistema debe recargar el tablero cada 20 segundos, salvo mientras el personal escribe un código. | [CA-08.3](historias-usuario.md#hu-08) | CT-08.3 |

## HU-09 · Registrar el avance de un pedido

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-24"></a>**RF-24** | El sistema debe registrar el avance Pendiente → En preparación → Listo para retirar con la hora de cada cambio, y rechazar saltos, retrocesos y cambios sobre pedidos entregados. | [CA-09.1](historias-usuario.md#hu-09), [CA-09.2](historias-usuario.md#hu-09) | CT-09.1, CT-09.2 |
| <a id="rf-25"></a>**RF-25** | El sistema debe detectar dos cambios simultáneos sobre el mismo pedido, aplicar solo el primero y avisar a quien hizo el segundo. | [CA-09.3](historias-usuario.md#hu-09) | CT-09.3 |

## HU-10 · Entregar el pedido verificando el código

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-26"></a>**RF-26** | El sistema debe registrar la entrega solo si el pedido está Listo para retirar y el código presentado coincide, sin distinguir mayúsculas, espacios ni guion. | [CA-10.1](historias-usuario.md#hu-10), [CA-10.3](historias-usuario.md#hu-10) | CT-10.1, CT-10.3 |
| <a id="rf-27"></a>**RF-27** | El sistema debe mantener el pedido Listo para retirar cuando el código no coincide, con un aviso que identifique el pedido. | [CA-10.2](historias-usuario.md#hu-10) | CT-10.2 |

## HU-11 · Ingresar como personal

| RF | Requisito funcional | Criterios | Casos de prueba |
|---|---|---|---|
| <a id="rf-28"></a>**RF-28** | El sistema debe reservar el tablero y el menú del personal a quien ingrese con el usuario y la clave configurados, y cerrar esa sesión al salir. | [CA-11.1](historias-usuario.md#hu-11), [CA-11.2](historias-usuario.md#hu-11) | CT-11.1, CT-11.2 |
| <a id="rf-29"></a>**RF-29** | El sistema no debe arrancar si falta la clave del personal o tiene menos de 8 caracteres, y debe indicar cómo configurarla. | [CA-11.3](historias-usuario.md#hu-11) | CT-11.3 |
