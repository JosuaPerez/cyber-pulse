# CyberPulse 🛡️

Sistema automatizado de threat intelligence y alertas tempranas de ciberseguridad, en español, para la comunidad InfoSec, estudiantes y equipos de Blue Team.

**[@CyberPulse89 en Instagram](https://www.instagram.com/cyberpulse89/)**

## Qué hace

CyberPulse monitorea fuentes de noticias de ciberseguridad en inglés, analiza cada hallazgo con un modelo de lenguaje (con validación anti-alucinación contra la fuente original), genera un carrusel visual y lo publica automáticamente en Instagram.

1. **Monitoreo** — Lee RSS de fuentes como The Hacker News, BleepingComputer, Krebs on Security, Dark Reading y SecurityWeek.
2. **Análisis con verificación** — Gemini extrae y traduce el hallazgo al español, pero cada CVE, CVSS y versión mencionados se valida contra el texto original de la fuente antes de aceptarse. Si el modelo no puede justificar un dato con la fuente, se rechaza y se reintenta.
3. **Generación visual** — Un frontend en React + Vite renderiza las 5 slides del carrusel; Playwright las captura como imágenes.
4. **Publicación** — Las imágenes se suben a Cloudflare R2 y se publican como carrusel en Instagram vía la Graph API de Meta.
5. **Persistencia** — Cada noticia se registra en SQLite con su estado (detectada → analizada → renderizada → publicada), evitando duplicados y permitiendo reintentos seguros ante fallos.

## Arquitectura

```
cyberpulse-bot/          # Backend Python: monitoreo, análisis, publicación
  app/
    lector_rss.py        # Lectura y deduplicación de feeds RSS
    analizador.py         # Prompt + validación anti-alucinación con Gemini
    esquemas.py            # Esquema Pydantic de la salida del análisis
    glosario.py            # Reglas de traducción y estilo español
    generador.py            # Orquesta a Playwright para renderizar las slides
    almacenamiento_r2.py     # Subida de imágenes a Cloudflare R2
    historial_db.py           # Persistencia de estado en SQLite
    bot_cyberpulse.py          # Orquestación del ciclo y publicación en Meta
    config.py                   # Configuración centralizada (variables de entorno)
  tests/                  # Suite de tests (pytest)

cyberpulse-templates/    # Frontend React + Vite: plantillas visuales del carrusel
```

Ambos servicios corren en contenedores Docker separados, conectados por una red interna (`docker-compose.yml`).

## Stack

- **Backend:** Python, Google Gemini API, SQLite, Playwright, Docker
- **Frontend:** React, Vite, Tailwind CSS
- **Almacenamiento:** Cloudflare R2 (S3-compatible)
- **Publicación:** Meta Graph API (Instagram)

## Principios de diseño

- **Nunca publicar sin verificar.** Ningún CVE, CVSS o afirmación específica se publica si no aparece literalmente en la fuente original.
- **Nunca inflar severidad.** El nivel de certeza de la fuente (confirmado / posible / sin evidencia) se preserva en la traducción.
- **Fail-safe, no fail-silent.** Cada etapa del pipeline (red, IA, renderizado, publicación) tiene manejo explícito de errores, reintentos con backoff, y el estado queda siempre registrado.

## Configuración local

1. Copia `.env.example` a `.env` en `cyberpulse-bot/` y completa tus credenciales (ver esa plantilla para la lista completa).
2. `docker compose up --build` desde `cyberpulse-bot/`.
3. Por defecto, `DRY_RUN=true`: el bot genera todo el contenido pero no publica nada, dejando una vista previa en `media/post_pendiente.txt` para revisión manual.

## Estado del proyecto

Proyecto activo y en desarrollo, mantenido por su autor como parte de su formación en ciberseguridad.

## Licencia

MIT — ver [LICENSE](LICENSE).
