# Registro de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado

- Dominio con las reglas de negocio RN-NEG-01 a RN-NEG-07: pedidos, estados, código de retiro
  sin caracteres ambiguos, total calculado y precio fijo al confirmar.
- Persistencia en SQLite con control optimista del estado y regeneración del código de retiro
  si se repite.
- Interfaz del cliente: menú con total en vivo, revisión, confirmación con código de retiro,
  seguimiento del estado, mis pedidos, registro e ingreso con correo y cédula.
- Interfaz del personal: tablero por estado, avance de pedidos, entrega con verificación del
  código y mantenimiento del menú.
- API `/health` y `/api/v1/productos`, con documentación OpenAPI en `/docs`.
- Imagen Docker con healthcheck, `compose.yaml` con volumen nombrado, e integración continua en
  GitHub Actions.

### Corregido

- DEF-01: las fuentes WOFF2 se servían como `application/octet-stream` dentro de la imagen.
- DEF-02: el resumen del tablero no usaba el plural ("2 pendiente").
- DEF-03: el aviso de código incorrecto no identificaba el pedido.
