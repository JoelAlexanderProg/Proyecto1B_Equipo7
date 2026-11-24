# 6. Casos de prueba y resultados

| Documento | Contenido |
|---|---|
| Este plan | Alcance, estrategia, niveles, técnicas, entorno y criterios |
| [Catálogo de casos](casos-de-prueba.md) | Cada caso `CT-XX.Y` con su criterio, técnica, nivel, pruebas y resultado |
| [Ejecución](ejecucion.md) | Resultados de la versión 1.0.0, casos manuales con sus ejecuciones y evidencias |
| [Defectos](defectos.md) | DEF-01 a DEF-04: reproducción, análisis, solución, nueva ejecución y base de conocimiento |

La documentación de pruebas sigue la semana 5 [6]: plan (alcance, estrategia, recursos,
calendario), casos (precondiciones, entradas, pasos, resultado esperado), ejecución (resultado
obtenido y evidencia) y defectos (reproducción, impacto, estado).

## 6.1 Objetivo y alcance

Encontrar defectos antes de la entrega y demostrar que el Release 1.0 cumple los 37 criterios de
aceptación, las 7 reglas de negocio y los 7 requisitos no funcionales. Como dice Myers (citado por
Pressman [1]), una prueba exitosa es la que descubre un error. Por eso los casos se diseñaron desde
los criterios de aceptación, antes de conocer el resultado, y no se ajustaron para que pasaran.

**Fuera de alcance:** rendimiento con carga real, compatibilidad con navegadores antiguos y pruebas
de seguridad ofensivas.

## 6.2 Estrategia

Las pruebas van de lo pequeño a lo grande (principio 4 de Davis [1]) y el esfuerzo se concentra
donde se esperan más defectos: el dominio y el flujo de estados (principios 3 y 6).

| Nivel | Qué verifica | Herramienta | Casos ejecutados |
|---|---|---|---|
| Unitaria | Reglas del dominio, validaciones, código de retiro, configuración | pytest | 60 |
| Integración | Servicios con SQLite real en un archivo temporal | pytest + `tmp_path` | 17 |
| Sistema | Recorridos completos por HTTP con sesión, como un navegador | pytest + `TestClient` de FastAPI | 36 |
| Manual asistida | Interfaz a 360 y 1280 px, contenedor, persistencia, recarga del tablero, análisis estático | Playwright, Docker CLI, SonarQube | 6 casos (CT-M01 a CT-M06) |
| Aceptación | Recorrido de PN-01 y PN-02 frente al cliente | Demostración en la presentación | — |

Con la parametrización de pytest, 81 funciones de prueba generan 113 ejecuciones.

## 6.3 Técnicas de diseño de casos

Pressman cap. 23 [1] e ISTQB [18]:

| Técnica | Dónde se aplica | Ejemplo |
|---|---|---|
| Partición de equivalencia | Cantidades, precios, cédula, celular, correo | Cantidad: válida {1…20}; inválidas {≤ 0}, {> 20}, {no entero}, {texto}, {booleano} |
| Valores límite | Cantidad y precio | 0, **1**, **20**, 21 · 0,00, **0,01**, **100,00**, 100,01 |
| Transición de estados | RN-NEG-06 | Las 3 transiciones válidas y todas las inválidas: saltar, retroceder, avanzar desde Listo sin código, cambiar un pedido Entregado |
| Tabla de decisión | RN-NEG-07 | (estado = Listo) × (código correcto): solo la combinación sí × sí entrega |
| Escenarios de uso | PN-01, PN-02 | Recorrido completo del cliente y del personal |
| Revisión visual con medición | RNF-02, RNF-06 | Alto de cada control y desplazamiento horizontal a 360 px |

## 6.4 Entorno

| Elemento | Valor |
|---|---|
| Código bajo prueba | Etiqueta `v1.0.0` (commit `46a63f9`) |
| Equipo | Windows 11, Python 3.12.10, pytest 9.2.0 |
| CI | GitHub Actions `ubuntu-latest`, Python 3.12 |
| Contenedor | Imagen `cafeteria-app:1.0.0` en Docker 29.9.3 |
| Datos | Base SQLite temporal por prueba, con el menú de demostración de 10 productos |

## 6.5 Criterios

- **Entrada:** el código compila, Ruff no tiene observaciones y la base de prueba se crea vacía.
- **Salida:** 100 % de los casos aprobados, ningún defecto abierto de severidad crítica o fatal,
  cobertura ≥ 80 % y Quality Gate aprobado.
- **Caso que falla:** se registra un reporte `DEF-XX` (Issue con la plantilla de la semana 7) con
  pasos, severidad y fase de origen. Se analiza la causa (error → defecto → fallo, IEEE 610 [5]),
  se corrige en una rama `fix/` con un PR enlazado y se vuelve a ejecutar el caso junto con la
  regresión completa (principio 9 de Davis [1]).

## 6.6 Calendario

| Fecha | Actividad |
|---|---|
| 24-11-2026 | Pruebas unitarias del dominio (escritas junto con las reglas) |
| 24-11-2026 | Pruebas de integración y de sistema por cada PR |
| 24-11-2026 | Casos manuales CT-M01 a CT-M06 y corrección de DEF-01 a DEF-04 |
| 24-11-2026 | Ejecución final sobre `v1.0.0` |
| 27-11-2026 | Prueba de aceptación en la presentación al cliente |
