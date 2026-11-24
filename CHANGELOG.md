# Registro de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

## [1.0.0] - 2026-11-24

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

### Cambiado

- Correcciones del análisis de SonarQube (perfil Sonar way comprehensive): constantes para las
  rutas repetidas, `Number.parseInt` en el JavaScript, `Cliente.con_identidad`, sin
  `response_model` redundante en la API y una prueba con una sola llamada que puede fallar.
- Rama `main` protegida: Pull Request obligatorio y CI en verde para integrar.

### Corregido

- DEF-01: las fuentes WOFF2 se servían como `application/octet-stream` dentro de la imagen.
- DEF-02: el resumen del tablero no usaba el plural ("2 pendiente").
- DEF-03: el aviso de código incorrecto no identificaba el pedido.
- Rutas alternativas sin prueba detectadas por el Quality Gate (cobertura del código nuevo
  75,9 %): 9 pruebas de sistema nuevas; cobertura total 97,2 %.

[Sin publicar]: https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/JoelAlexanderProg/Proyecto1B_Equipo7/releases/tag/v1.0.0
