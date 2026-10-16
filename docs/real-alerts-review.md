# Prueba con noticias reales · revisión 14/10/2026

Muestras locales de quince diapositivas, sin IA ni publicación, en
`/?preview=real-alerts&variant=update&slide=1`. Variantes: `update`, `editorial`,
`context`; diapositivas del 1 al 5. No cambia la variante predeterminada del bot.

## Fuentes y límites editoriales

- A: [Mozilla MFSA 2026-106](https://www.mozilla.org/en-US/security/advisories/mfsa2026-106/),
  publicado el 13/10/2026, impacto alto y Firefox 158 como versión corregida.
  No se afirma explotación activa. La captura representa ese aviso, no todas
  las ramas ESR ni el estado de actualización de un equipo concreto.
- B: [Huntress, Adversary Tactics, septiembre de 2026](https://www.huntress.com/threat-library/adversary-tactics/september-2026),
  sección Power BI Phishing Delivers Rogue ScreenConnect Clients. Campaña
  observada, no vulnerabilidad de Power BI; no se afirma actividad vigente hoy
  ni se asigna una severidad no aportada por la fuente.
- C: [Discord, incidente de un proveedor de atención al cliente](https://discord.com/press-releases/update-on-security-incident-involving-third-party-customer-service),
  publicado el 03/10/2025, actualizado el 09/10/2025. Es un caso histórico, no
  una alerta nueva. Se atribuyen alcance y exclusiones a Discord; no se identifica
  al proveedor ni se amplifican cifras o afirmaciones de los atacantes.

Las medidas de consulta de versión y verificación por canal oficial son
recomendaciones editoriales; no se presenta una acción general como prueba de
compromiso individual. Los campos que no tengan clasificación permanecen sin
clasificar. Cada diapositiva incluye fecha, fuente y rótulo de prueba visual.
Antes de publicar, revalidar las fuentes y el estado actual; el caso C debe
mantener siempre la marca histórica.

## Exportación

Con Vite activo en 127.0.0.1:5173, desde la raíz:

```powershell
.\.venv\Scripts\python.exe cyberpulse-templates/scripts/render-real-alerts.py
```

Genera tres directorios con cinco PNG 1080 × 1350 y contacto visual en
`cyberpulse-bot/media/real-alerts-2026-10-14/`, excluido de Git. Bloquea
solicitudes externas y comprueba atribución, errores de JavaScript y encuadre.
