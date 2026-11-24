# Cómo contribuir a CaféPoli

Acuerdos del Equipo 7 para trabajar en el repositorio. El detalle y su justificación están en
`docs/03-ambiente-desarrollo` de la rama `documentacion`.

## Flujo de trabajo

1. Todo cambio empieza en una **Issue**: historia de usuario, solicitud de cambio (CR) o reporte
   de problema (DEF), con sus plantillas.
2. Se crea una **rama** desde `main` con el prefijo del tipo de cambio:

   | Prefijo | Uso | Destino |
   |---|---|---|
   | `feature/` | Nueva funcionalidad (HU) | `main` |
   | `fix/` | Corrección de un defecto (DEF) | `main` |
   | `chore/` | Configuración, plantillas, dependencias | `main` |
   | `hotfix/` | Corrección urgente sobre una versión publicada | `main` |
   | `docs/` | Documentación del proyecto | `documentacion` |

3. **Commits** pequeños, con un título en español en modo indicativo que describe el cambio.
4. **Pull Request** con la plantilla: objetivo, Issue vinculada, cambios y evidencia de pruebas.
5. La integración continua (Ruff, pytest y construcción de la imagen) debe estar en verde antes
   de integrar. Se integra con *merge commit* y se borra la rama.

## Estándares de código

- PEP 8 verificado con Ruff (`ruff check` y `ruff format`), líneas de hasta 100 caracteres.
- Docstrings estilo Google en todo lo público: `Args`, `Returns`, `Raises` (equivalentes a
  `@param`, `@return` y `@throws` de JavaDoc).
- Las reglas de negocio viven en `cafeteria.dominio`; las rutas solo traducen HTTP.
- Nombres del dominio en español, iguales a los de la especificación del cliente.

## Pruebas

```powershell
.venv\Scripts\python -m pytest --cov
```

Toda regla de negocio nueva o modificada lleva su prueba. Un defecto corregido lleva una prueba
que antes fallaba.

## Versionado

Versionado semántico (`MAJOR.MINOR.PATCH`). Cada versión publicada es una etiqueta `vX.Y.Z` en
`main` (línea base) y se registra en `CHANGELOG.md`.
