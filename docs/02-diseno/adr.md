# Decisiones de arquitectura (ADR)

Formato de la semana 5 [6], basado en Nygard [8]: contexto, decisión, consecuencias, estado y fecha.
Todas están **aceptadas** para el Release 1.0 desde el 24-11-2026.

## ADR-001 · Python 3.12 con FastAPI

- **Contexto.** El equipo domina Python. La aplicación necesita páginas web para el cliente y el
  personal, una API pequeña y documentación técnica del código.
- **Decisión.** Python 3.12 con FastAPI, Jinja2 y Uvicorn.
- **Alternativas.** Flask (más simple, pero sin documentación OpenAPI automática); aplicación de
  escritorio con Tkinter (no permite pedir desde el celular ni encaja con Docker).
- **Consecuencias.** OpenAPI en `/docs` sin esfuerzo adicional; validación de formularios con
  `Form`; `TestClient` para pruebas de sistema. A cambio, las rutas asíncronas exigen cuidado al
  leer formularios dinámicos.

## ADR-002 · Arquitectura en capas con puertos

- **Contexto.** Las siete reglas de negocio deben poder demostrarse y probarse ([especificación
  §8]); la semana 4 advierte sobre reglas dispersas (*Shotgun Surgery*).
- **Decisión.** Cuatro capas (presentación, aplicación, dominio, infraestructura). El dominio no
  importa nada externo; la aplicación define protocolos de repositorio que la infraestructura
  implementa.
- **Consecuencias.** 57 pruebas unitarias del dominio se ejecutan en milisegundos. Cambiar SQLite
  por otro motor solo afecta a `infraestructura`. Hay más archivos que en un diseño plano.

## ADR-003 · SQLite con `sqlite3` de la biblioteca estándar, en un volumen Docker

- **Contexto.** La información debe persistir entre ejecuciones (§8); una sola cafetería, carga
  baja; el despliegue debe ser de un solo comando.
- **Decisión.** SQLite en modo WAL, con el módulo `sqlite3` y SQL explícito en los repositorios.
  En Docker, el archivo vive en el volumen nombrado `cafeteria-data` (práctica 1).
- **Alternativas.** PostgreSQL (otro contenedor y más configuración, innecesario para la carga);
  un ORM (una dependencia más para cuatro tablas).
- **Consecuencias.** Cero servicios adicionales y respaldo copiando un archivo. Las restricciones
  `UNIQUE` y `CHECK` refuerzan las reglas. No escala a varios servidores; si hiciera falta, ADR-002
  limita el cambio a la infraestructura.

## ADR-004 · Código de retiro de 6 caracteres sin ambiguos

- **Contexto.** RN-04 pide reducir confusiones en la entrega y RN-NEG-05 exige un código único.
- **Decisión.** 6 caracteres de un alfabeto de 31 símbolos sin 0/O ni 1/I/L, con formato `XXX-XXX`,
  generados con `secrets`. La unicidad la garantiza la base de datos y el servicio reintenta si el
  código se repite. Al entregar se acepta en minúsculas, con espacios o sin guion.
- **Consecuencias.** 887 millones de combinaciones; el código se dicta y se lee sin confusiones.
  Un número correlativo habría sido más corto, pero predecible: cualquiera podría adivinar el
  código de otro cliente.

## ADR-005 · Tabla de transiciones y control optimista del estado

- **Contexto.** RN-NEG-06 fija un orden estricto, y dos personas del personal pueden atender el
  mismo pedido a la vez.
- **Decisión.** El siguiente estado sale de una tabla (`_SIGUIENTE_ESTADO`) y no de condicionales.
  El `UPDATE` solo se aplica si el estado sigue siendo el que se leyó.
- **Consecuencias.** No se pierden actualizaciones ni se saltan estados. El segundo usuario recibe
  «El pedido cambió de estado mientras lo atendías».

## ADR-006 · Sesión firmada; cliente sin contraseña y personal por variable de entorno

- **Contexto.** La especificación identifica al cliente por código y datos personales (§7) y no
  pide autenticación. El personal sí debe estar protegido.
- **Decisión.**
  - Cookie de sesión firmada (`SessionMiddleware`, `SameSite=Lax`, 8 horas).
  - El cliente ingresa con correo y cédula (supuesto A1).
  - El personal usa una cuenta definida en `.env`; la clave se compara en tiempo constante
    (`hmac.compare_digest`).
- **Consecuencias.**
  - Ingreso rápido para el cliente.
  - Riesgo aceptado: quien conozca el correo y la cédula de otra persona puede ver sus pedidos, no
    modificarlos. Se reevaluará en un próximo release.
  - Las variables de entorno no son un almacén seguro de secretos (semana 3); por eso `.env` está
    fuera del repositorio.

## ADR-007 · GitHub Flow con una rama de documentación

- **Contexto.** La docente pide el código estable en `main` y la documentación en `documentacion`.
  La semana 5 propone GitHub Flow: Issue, rama, commits, Pull Request, revisión y merge.
- **Decisión.**
  - Ramas cortas `feature/`, `fix/` y `chore/` hacia `main`, con PR y CI obligatoria (rama
    protegida).
  - Ramas `docs/` hacia `documentacion`, que se sincroniza con `main` en cada línea base `vX.Y.Z`.
- **Consecuencias.** `main` siempre es desplegable. La documentación se versiona junto con la línea
  base que describe. Detalle en [flujo de trabajo](../03-ambiente-desarrollo/flujo-de-trabajo.md).

## ADR-008 · Páginas en el servidor con mejora progresiva, sin framework de JavaScript

- **Contexto.** El equipo no necesita una SPA, el equipo de desarrollo no tiene Node y la app debe
  funcionar en celulares con conexión limitada.
- **Decisión.**
  - Plantillas Jinja2, una hoja de estilos propia con variables CSS y un archivo JavaScript de unas
    60 líneas.
  - Las fuentes se sirven desde la propia app.
- **Consecuencias.**
  - Sin paso de compilación. El servidor valida todo, así que el JavaScript solo mejora la
    experiencia.
  - Ese script no tiene pruebas automáticas en el Release 1.0: se excluye de la cobertura y se
    verifica con el caso manual CT-M01.
