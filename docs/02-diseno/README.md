# 2. Documentación de diseño

Arquitectura, diseño detallado y decisiones del Release 1.0. Las decisiones con sus alternativas y
consecuencias están en los [ADR](adr.md).

## 2.1 Arquitectura de alto nivel

CaféPoli es una aplicación web con **arquitectura en capas** (ADR-002). Cada capa solo depende de
la inferior, y la persistencia se invierte con puertos: los servicios dependen de protocolos que la
infraestructura implementa. Las reglas de negocio quedan aisladas en el dominio.

```mermaid
flowchart TB
    subgraph Navegadores
        C["Cliente · celular"]
        P["Personal · tablet o PC"]
    end
    subgraph Contenedor["Contenedor Docker · cafeteria-app:1.0.0 · puerto 8000"]
        direction TB
        subgraph Presentacion["Presentación · FastAPI + Jinja2"]
            RC["rutas_cliente"]
            RP["rutas_personal"]
            RA["rutas_api · /health · /api/v1"]
        end
        subgraph Aplicacion["Aplicación"]
            SM["ServicioMenu"]
            SC["ServicioClientes"]
            SPd["ServicioPedidos"]
            SA["ServicioAccesoPersonal"]
            PU[["puertos: RepositorioProductos · Clientes · Pedidos"]]
        end
        subgraph Dominio["Dominio · sin dependencias externas"]
            M["Producto · Cliente · Pedido · DetallePedido · EstadoPedido"]
            CR["codigo_retiro · validaciones · excepciones"]
        end
        subgraph Infra["Infraestructura"]
            RS["Repositorios SQLite"]
            BD["BaseDatos · esquema"]
        end
    end
    V[("Volumen cafeteria-data<br/>/app/data/cafeteria.db")]
    C -- HTTP --> RC
    P -- HTTP --> RP
    RC & RP & RA --> SM & SC & SPd & SA
    SM & SC & SPd --> PU
    SM & SC & SPd --> M
    RS -. implementa .-> PU
    RS --> M
    RS --> BD --> V
```

| Capa | Paquete | Responsabilidad | Depende de |
|---|---|---|---|
| Presentación | `cafeteria.presentacion` | Traducir HTTP a llamadas de servicio, sesiones, plantillas, API | Aplicación |
| Aplicación | `cafeteria.aplicacion` | Casos de uso: obtener datos, invocar el dominio, guardar | Dominio y puertos |
| Dominio | `cafeteria.dominio` | Entidades y reglas RN-NEG-01 a 07 | Nada (biblioteca estándar) |
| Infraestructura | `cafeteria.infraestructura` | SQLite, repositorios, menú de demostración | Dominio y puertos |

**Por qué en capas.** Pressman identifica las capas (*layering*) como la clave de la abstracción:
separan los conceptos del diseño de los detalles de implementación y reducen la complejidad [1].
En la práctica, la regla RN-NEG-07 vive en `Pedido.entregar` y se prueba sin servidor ni base de
datos. La semana 4 advierte sobre *Feature Envy* y *Shotgun Surgery*: si las reglas se repartieran
entre rutas y plantillas, un cambio de regla obligaría a tocar muchos archivos [2], [3].

## 2.2 Despliegue

```mermaid
flowchart LR
    subgraph Host["Equipo de la cafetería · Docker Engine"]
        subgraph Cont["contenedor cafepoli · usuario sin privilegios"]
            U["uvicorn · python -m cafeteria"]
        end
        Vol[("volumen cafeteria-data")]
        Env[".env · clave del personal"]
    end
    N1["Celulares de clientes"] -- "http :8000" --> U
    N2["Mostrador"] -- "http :8000" --> U
    U --- Vol
    Env -. variables .-> U
    D["Docker"] -. "HEALTHCHECK /health cada 30 s<br/>restart: unless-stopped<br/>256 MB · 0,5 CPU" .-> Cont
```

## 2.3 Modelo de dominio

```mermaid
classDiagram
    direction LR
    class Producto {
        +codigo: str
        +nombre: str
        +categoria: Categoria
        +precio: Decimal
        +disponible: bool
        +actualizar(nombre, categoria, precio, disponible)
    }
    class Cliente {
        <<frozen>>
        +codigo: str
        +nombre: str
        +apellido: str
        +cedula: str
        +celular: str
        +correo: str
        +nuevo(...)$ Cliente
        +con_identidad(id, codigo) Cliente
    }
    class Pedido {
        +codigo_retiro: str
        +cliente_id: int
        +estado: EstadoPedido
        +fecha_registro: datetime
        +confirmar(cliente_id, seleccion, codigo)$ Pedido
        +total() Decimal
        +avanzar()
        +entregar(codigo)
    }
    class DetallePedido {
        <<frozen>>
        +producto_codigo: str
        +producto_nombre: str
        +cantidad: int
        +precio_unitario: Decimal
        +subtotal() Decimal
    }
    class EstadoPedido {
        <<enumeration>>
        PENDIENTE
        EN_PREPARACION
        LISTO_PARA_RETIRAR
        ENTREGADO
        +siguiente() EstadoPedido
    }
    class Categoria {
        <<enumeration>>
        ALIMENTO
        BEBIDA
    }
    Cliente "1" --> "*" Pedido : realiza
    Pedido "1" *-- "1..*" DetallePedido : contiene
    DetallePedido "*" ..> "1" Producto : copia precio y nombre
    Pedido --> EstadoPedido
    Producto --> Categoria
```

Decisiones que previenen *code smells* desde el diseño (semana 4 [6], Fowler [3]):

| Riesgo | Decisión | Refactorización de referencia |
|---|---|---|
| *Primitive Obsession*: estado como texto, dinero como `float` | `EstadoPedido` y `Categoria` son enumeraciones; montos con `Decimal` | Replace Primitive with Object |
| *Mutable Data*: el precio del pedido cambia con el menú | `DetallePedido` congelado, sin *setters* (RN-NEG-04) | Remove Setting Method |
| Total guardado que se desincroniza | `Pedido.total` se calcula desde los detalles (RN-NEG-03) | Replace Derived Variable with Query |
| *Data Clumps*: datos del cliente sueltos | Entidad `Cliente` con fábrica validada | Introduce Parameter Object |
| Condicional largo para los estados | Tabla `_SIGUIENTE_ESTADO` | Decompose Conditional |
| `None` revisado en cada llamada | Excepciones de negocio (`PedidoNoEncontrado`) | Introduce Special Case |
| Suposiciones implícitas | Validación en constructores y fábricas | Introduce Assertion |

## 2.4 Ciclo de vida del pedido

```mermaid
stateDiagram-v2
    direction LR
    state "En preparación" as EnPreparacion
    state "Listo para retirar" as Listo
    [*] --> Pendiente : cliente confirma
    Pendiente --> EnPreparacion : avanzar()
    EnPreparacion --> Listo : avanzar()
    Listo --> Entregado : entregar(código correcto)
    Listo --> Listo : entregar(código incorrecto) / rechazo
    Entregado --> [*]
```

Cualquier otra transición (saltar un estado, retroceder, avanzar desde Listo sin código o cambiar un
pedido entregado) lanza `TransicionNoPermitida`. El repositorio guarda el cambio con la condición
`WHERE estado = <estado anterior>` (control optimista): si otra persona ya lo cambió, el segundo
cambio se rechaza (ADR-005).

## 2.5 Secuencias

### PN-01 · Confirmar un pedido

```mermaid
sequenceDiagram
    actor Cl as Cliente
    participant R as rutas_cliente
    participant S as ServicioPedidos
    participant D as Pedido (dominio)
    participant Rp as RepositorioPedidosSQLite
    Cl->>R: POST /pedido/revisar (cantidades)
    R->>S: revisar(cantidades)
    S->>D: construir_detalles(selección)
    D-->>S: detalles + total (RN-NEG-01, 02, 03)
    R-->>Cl: revisión con total y total_revisado oculto
    Cl->>R: POST /pedido/confirmar (total_revisado)
    R->>S: revisar(borrador de la sesión)
    alt el total cambió
        R-->>Cl: muestra el nuevo total, no confirma (RU-03)
    else el total coincide
        R->>S: confirmar(cliente, cantidades)
        loop hasta 5 intentos
            S->>D: Pedido.confirmar(código aleatorio)
            S->>Rp: agregar(pedido)
            alt código repetido
                Rp-->>S: CodigoRetiroDuplicado
            else guardado
                Rp-->>S: pedido con id
            end
        end
        R-->>Cl: 303 → /pedidos/K7P-4QX
    end
```

### PN-02 · Entregar un pedido

```mermaid
sequenceDiagram
    actor Pe as Personal
    participant R as rutas_personal
    participant S as ServicioPedidos
    participant D as Pedido (dominio)
    participant Rp as RepositorioPedidosSQLite
    Pe->>R: POST /personal/pedidos/{id}/entregar (código del cliente)
    R->>S: entregar(id, código)
    S->>Rp: obtener(id)
    S->>D: entregar(código)
    alt no está Listo o el código no coincide
        D-->>S: TransicionNoPermitida / CodigoRetiroIncorrecto
        R-->>Pe: aviso «Pedido XXX-XXX: no se registró la entrega…»
    else correcto
        S->>Rp: actualizar_estado(pedido, LISTO_PARA_RETIRAR)
        R-->>Pe: aviso «Pedido XXX-XXX entregado.»
    end
```

## 2.6 Modelo de datos

```mermaid
erDiagram
    CLIENTES ||--o{ PEDIDOS : realiza
    PEDIDOS ||--|{ DETALLES_PEDIDO : contiene
    PRODUCTOS ||--o{ DETALLES_PEDIDO : "se pide en"
    PRODUCTOS {
        int id PK
        text codigo UK "ALI-001"
        text nombre
        text categoria "ALIMENTO | BEBIDA"
        int precio_centavos "> 0"
        int disponible "0 | 1"
    }
    CLIENTES {
        int id PK
        text codigo UK "CLI-0001"
        text nombre
        text apellido
        text cedula UK
        text celular
        text correo UK
    }
    PEDIDOS {
        int id PK
        text codigo_retiro UK "XXX-XXX"
        int cliente_id FK
        text estado "CHECK en 4 valores"
        text fecha_registro "ISO 8601 -05:00"
        text fecha_preparacion
        text fecha_listo
        text fecha_entrega
    }
    DETALLES_PEDIDO {
        int id PK
        int pedido_id FK
        text producto_codigo FK
        text producto_nombre "copia al confirmar"
        int cantidad "> 0"
        int precio_unitario_centavos "copia al confirmar"
    }
```

Los montos se guardan como centavos enteros para evitar errores de redondeo; las fechas, en ISO 8601
con zona horaria, para que se comparen correctamente como texto. Las restricciones `UNIQUE` y
`CHECK` repiten en la base de datos las reglas más críticas (código único, estados válidos,
cantidades positivas) como segunda barrera.

## 2.7 Interfaces

**Web.** Páginas renderizadas en el servidor (Jinja2) con mejora progresiva (ADR-008): sin
JavaScript la aplicación funciona igual, y el script solo agrega el total en vivo y la recarga del
tablero. El diseño visual parte de la propuesta estética del equipo:

- Paleta café (`#7B4B2A`) sobre fondo neutro, con cuatro colores de estado separados del color de
  marca: ámbar, azul, verde y gris. Todos tienen contraste ≥ 5,5:1.
- Tipografías Space Grotesk, Inter y JetBrains Mono (licencia OFL), servidas por la propia app.
- El cliente usa primero el celular; el personal trabaja en un tablero tipo kanban.

**API.** `GET /health` y `GET /api/v1/productos?disponibles=true`, documentadas con OpenAPI en
`/docs` ([documentación técnica](../04-documentacion-tecnica/README.md)).

**Rutas web.**

| Rol | Ruta | Propósito |
|---|---|---|
| Cliente | `GET /` · `POST /pedido/revisar` · `POST /pedido/confirmar` | Menú, revisión y confirmación |
| Cliente | `GET /pedidos/{código}` · `GET /mis-pedidos` | Seguimiento |
| Cliente | `GET/POST /registro` · `GET/POST /ingresar` · `POST /salir` | Cuenta |
| Personal | `GET /personal` · `POST /personal/pedidos/{id}/avanzar` · `.../entregar` | Tablero y atención |
| Personal | `GET/POST /personal/menu` · `GET/POST /personal/menu/{código}` · `.../disponibilidad` | Menú |
| Personal | `GET/POST /personal/ingresar` · `POST /personal/salir` | Acceso |
