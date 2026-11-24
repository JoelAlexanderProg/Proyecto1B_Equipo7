# Documentación de CaféPoli · Release 1.0

Documentación del proyecto IB de ISWD633 Construcción y Evolución de Software (EPN, 2026-B),
Equipo 7. El código estable está en la rama [`main`](../../../tree/main); esta rama,
`documentacion`, contiene los entregables del Release 1.0 y se sincroniza con `main` en cada
línea base.

| N.º | Entregable | Documento |
|---|---|---|
| 1 | Documentación de requisitos | [01-requisitos](01-requisitos/README.md): alcance, [historias de usuario](01-requisitos/historias-usuario.md), [requisitos funcionales](01-requisitos/requisitos-funcionales.md), reglas, requisitos no funcionales, supuestos y [matriz de trazabilidad](01-requisitos/matriz-trazabilidad.md) |
| 2 | Documentación de diseño | [02-diseno](02-diseno/README.md): arquitectura, diagramas y [decisiones de arquitectura (ADR)](02-diseno/adr.md) |
| 3 | Ambiente de desarrollo y flujo de trabajo | [03-ambiente-desarrollo](03-ambiente-desarrollo/README.md) y [flujo de trabajo](03-ambiente-desarrollo/flujo-de-trabajo.md) |
| 4 | Documentación técnica del código | [04-documentacion-tecnica](04-documentacion-tecnica/README.md) y [referencia HTML](04-documentacion-tecnica/html/cafeteria.html) |
| 5 | Reporte de análisis estático | [05-analisis-estatico](05-analisis-estatico/README.md) |
| 6 | Casos de prueba y resultados | [plan](06-pruebas/README.md), [casos](06-pruebas/casos-de-prueba.md), [ejecución](06-pruebas/ejecucion.md) y [defectos](06-pruebas/defectos.md) |
| 7 | Manual de instalación | [07-manual-instalacion.md](07-manual-instalacion.md) |
| 8 | Manual de usuario | [08-manual-usuario.md](08-manual-usuario.md) |

## Convenciones de identificadores

| Prefijo | Elemento | Ejemplo |
|---|---|---|
| `RN`, `RU`, `RN-NEG`, `PN` | Requisitos, reglas y procesos de la especificación del cliente v1.0 | RN-NEG-07 |
| `HU-XX` | Historia de usuario | HU-10 |
| `CA-XX.Y` / `CT-XX.Y` | Criterio de aceptación y caso de prueba que lo verifica | CA-10.2 / CT-10.2 |
| `CT-MXX` | Caso de prueba manual | CT-M03 |
| `RNF-XX` | Requisito no funcional | RNF-01 |
| `A-XX` | Supuesto o aclaración | A7 |
| `ADR-XXX` | Decisión de arquitectura | ADR-003 |
| `DEF-XX` | Reporte de problema (defecto) | DEF-01 |

## Referencias

Las referencias en formato IEEE que sustentan estas decisiones están en
[referencias.md](referencias.md).
