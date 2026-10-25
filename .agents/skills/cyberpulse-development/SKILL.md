---
name: cyberpulse-development
description: Implementa y verifica cambios en el bot Python y las plantillas React de CyberPulse, con ramas, pruebas y controles de publicación. Úsala para programación y mantenimiento del repositorio; no para redacción editorial aislada.
---

# CyberPulse development

## Establecer el estado real

Lee las instrucciones del repositorio y revisa rama, estado local y diff antes de editar. Verifica en los archivos actuales cualquier función, contrato o comando mencionado en planes anteriores.

Los cambios previos pertenecen al usuario: no los sobrescribas, descartes ni incluyas en commits propios por conveniencia. Trabaja en una rama `codex/` apropiada; reutiliza la rama de la tarea cuando corresponda. No crees worktrees por defecto. Ante una migración amplia con cambios pendientes, acuerda o crea un checkpoint recuperable dentro del alcance, sin capturar secretos ni archivos ajenos. Crear una rama sola no guarda cambios sin commit.

## Invariantes operativas

- No arranques Docker, el servicio completo o un scheduler para probar una plantilla. En este proyecto arrancarlos puede iniciar publicaciones reales. Primero inspecciona el punto de entrada y usa procesos aislados de renderizado/prueba.
- Configura modo seguro antes de importar módulos que carguen configuración. `DRY_RUN=true` es una barrera adicional, no garantía de que todas las rutas carecen de efectos externos. Usa directorios temporales o de salida separados y mocks para Gemini, Meta, R2 y otros servicios en pruebas.
- No muestres `.env`, tokens o credenciales en logs, diffs o commits. No cambies proveedor, modelos, permisos, programación ni configuración de producción salvo que la tarea lo incluya.
- Separa obtención de fuentes, análisis, validación, render y publicación. Conserva el rechazo de entradas no verificadas y el control de duplicados. Un fallo del modelo o del validador no justifica publicar un fallback sin verificación.
- Una revisión manual no debe recibir un sello de validación automática. No relajes controles para que pase un fixture concreto; demuestra que el caso inválido sigue rechazándose.

## Implementar y comprobar

Localiza el contrato y sus consumidores antes de cambiarlo. Referencias iniciales, que debes verificar en el árbol actual: `cyberpulse-bot/app/alertas_v3.py`, `app/editorial_alertas.py`, `app/limites.py`, `app/generador.py` y `cyberpulse-templates/src/DailyAlert.jsx`. Las rutas `app/` anteriores son relativas a `cyberpulse-bot/`.

Añade pruebas de comportamiento para errores corregidos: identidad coherente, evidencia ausente, duplicados, fallos parciales y bloqueo de publicación cuando sean relevantes. En diseño, revisa imágenes generadas además de pruebas de datos. No uses llamadas reales a proveedores como pruebas unitarias.

Lee `.github/workflows/ci.yml`, dependencias y scripts antes de elegir comandos. Como orientación, el CI actual usa:

- Backend, desde `cyberpulse-bot`: `python -m ruff check app tests` y `python -m pytest -q`, con modo seguro.
- Frontend, desde `cyberpulse-templates`: `npm run lint`, `npm test` y `npm run build`.
- Ejecuta también las pruebas de scripts modificados: el CI principal puede no incluirlas.

Usa el entorno instalado cuando sea adecuado y escala la verificación al cambio. No instales dependencias, actualices lockfiles o ejecutes auditorías con corrección automática sin necesidad. Si no puedes ejecutar una prueba, informa qué quedó sin verificar.

## Entrega y GitHub

Revisa diff, archivos nuevos y `git diff --check`. No afirmes que los checks remotos están verdes por haber pasado pruebas locales. Si la tarea incluye commit, selecciona archivos explícitamente; si incluye PR, presenta cambios, pruebas y riesgos. La petición de diagnosticar o revisar no autoriza por sí sola push, merge o publicación.

No fusiones ni borres ramas sin autorización aplicable. Cuando el usuario haya pedido borrarlas tras completar el PR, confirma primero el merge y la conservación del trabajo; un squash puede no aparecer como ancestro de la rama. No borres una rama con trabajo pendiente ni uses borrado forzado para resolver ambigüedad. La entrega debe distinguir cambios locales, commit, push, PR, merge y despliegue: ninguno implica automáticamente los demás.
