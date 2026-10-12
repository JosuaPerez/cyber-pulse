# Arquitectura de CyberPulse

## Objetivo

CyberPulse detecta noticias de ciberseguridad, genera contenido técnico en español, renderiza un carrusel y, cuando el modo seguro está desactivado, lo publica en redes sociales.

## Flujo principal

```text
RSS
  -> selección y deduplicación en SQLite
  -> extracción del artículo
  -> análisis estructurado con Gemini
  -> validación Pydantic y verificación contra la fuente
  -> renderizado React mediante Playwright
  -> subida de imágenes a Cloudflare R2
  -> publicación mediante Meta Graph API
  -> registro del resultado en SQLite
```

## Componentes

- `cyberpulse-bot/app/lector_rss.py`: descarga fuentes y registra candidatos.
- `cyberpulse-bot/app/analizador.py`: genera y valida el contenido de alertas.
- `cyberpulse-bot/app/analizador_educativo.py`: genera contenido educativo.
- `cyberpulse-bot/app/esquemas.py`: contrato Pydantic de la salida de IA.
- `cyberpulse-bot/app/generador.py`: renderiza las slides con Playwright.
- `cyberpulse-bot/app/almacenamiento_r2.py`: publica imágenes en R2.
- `cyberpulse-bot/app/bot_cyberpulse.py`: coordina el pipeline y Meta.
- `cyberpulse-bot/app/historial_db.py`: persistencia e idempotencia local.
- `cyberpulse-templates`: presentación React/Vite del carrusel.

## Límites de confianza

- RSS y artículos externos son datos no confiables.
- La respuesta del modelo es no confiable hasta superar Pydantic y las verificaciones deterministas.
- R2, Meta, X y Gemini son servicios externos que pueden responder tarde, parcialmente o de forma ambigua.
- Los secretos solo entran mediante variables de entorno y nunca forman parte del repositorio.

## Estado actual

El diseño está orientado a una única instancia. SQLite evita duplicados terminales, pero todavía no reserva trabajos de forma atómica para múltiples workers. Antes de escalar horizontalmente se requiere una máquina de estados con reclamación transaccional, reintentos limitados y reconciliación de publicaciones ambiguas.

## Principios operativos

1. `DRY_RUN=true` es el modo seguro predeterminado.
2. Ningún dato técnico generado se publica sin validación.
3. Un timeout externo no implica necesariamente que la operación haya fallado.
4. Los logs deben ser útiles sin contener secretos.
5. Los cambios funcionales deben incluir pruebas y una estrategia de rollback.

