# Contribuir a CyberPulse

## Preparación local

1. Crea una rama desde `main`.
2. Copia `cyberpulse-bot/.env.example` como `cyberpulse-bot/.env`.
3. Usa únicamente credenciales propias y mantén `DRY_RUN=true`.
4. Instala las dependencias del backend con `pip install -r cyberpulse-bot/requirements-dev.txt`.
5. Instala el frontend con `npm ci` dentro de `cyberpulse-templates`.

## Comprobaciones obligatorias

Backend:

```powershell
cd cyberpulse-bot
python -m ruff check app tests
python -m pytest -q
```

Frontend:

```powershell
cd cyberpulse-templates
npm run lint
npm run build
npm audit --omit=dev --audit-level=high
```

## Pull requests

Mantén cada PR enfocada en un solo objetivo. Incluye pruebas para los cambios funcionales, instrucciones de migración cuando cambie SQLite o la configuración y un plan de rollback.

Nunca incluyas `.env`, bases de datos locales, imágenes generadas, tokens o respuestas completas de APIs que puedan contener credenciales.

