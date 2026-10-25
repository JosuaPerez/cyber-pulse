# Reel Mito vs. mecanismo · versión 3

Estado: implementado para revisión local, no publicado ni programado. El v2 de 29 s y su HTML original se conservan como historial. El guion activo es ahora el JSON de seis escenas de 19 s.

## Arquitectura real y alcance

Este piloto usa HTML autónomo + Playwright, no React/Vite. Se conserva esa arquitectura, sin modificar alertas, carruseles, feed, proveedores compartidos, Dockerfile ni compose. El antiguo script de construcción es ahora una entrada compatible a módulos pequeños en `cyberpulse-bot/app/reels/`:

- `settings.py`: constantes 1080×1920, carga y validación del JSON, flags y márgenes.
- `audio.py`: MoviePy para silencio/mezcla, Edge TTS por escena mediante el adaptador existente. Timeout total de voz: 120 s.
- `preview.py`: HTML autónomo, fuentes locales, caption y comprobación visual.
- `render.py`: capturas nativas a escala 1, codificación FFmpeg y verificación completa.
- `myth.py`: CLI y coordinación, sin importaciones del publicador.
- `check.py`: comprobación técnica de un MP4 existente.

Plantilla activa: `cyberpulse-bot/content/reels/phishing-myth-v3.html`. Fuentes tipográficas locales copiadas del proyecto a `content/reels/fonts/` para que estén dentro del contexto Docker; no se necesitan Vite, CDN ni descargas de fuentes.

## Escenas editables

Editar `cyberpulse-bot/content/reels/phishing-myth.json`, lista `scenes`: duración, tipo visual, titular, narración, detalle y textos del mockup. No hay que tocar Python para cambiar el guion dentro de los tipos visuales admitidos.

| Inicio–fin sin voz | Escena |
| --- | --- |
| 0–2 | No hacer clic no siempre te salva; SMS, cursor sin pulsar |
| 2–5 | Adjunto inesperado |
| 5–8 | Llamada que pide datos |
| 8–11 | QR → web que pide datos; esquema no escaneable |
| 11–16 | Verifica por otro canal; app oficial y check animado |
| 16–19 | Guárdalo; pregunta y opciones 1–4 |

Los cambios de escena son cortes; la entrada dura 0,18 s. Hay movimiento continuo de elementos. Los últimos 0,18 s recuperan el estado inicial, y el último frame exportado es idéntico al primero. No se funde una frase de voz con otra: el bucle es visual. El cierre enumera 1 SMS, 2 adjunto, 3 llamada, 4 QR; «Trampa 1–3» enumera solo las tres alternativas al enlace, no las respuestas de la encuesta.

## Flags y contrato

| Variable | Valor por defecto | Uso |
| --- | --- | --- |
| REEL_AUDIO | none | none, voice o music; nunca sustitución silenciosa de un fallo |
| REEL_DRAFT_LABEL | false | true muestra BORRADOR dentro del área segura |
| REEL_FPS | 24 | 24 o 30 |
| REEL_VIDEO_MBPS | 5 | Mínimo 4; CBR con relleno para no exportar texto a 270 kbps |
| REEL_SAFE_TOP | 0.14 | Margen superior; no puede reducirse por debajo del 14 % |
| REEL_SAFE_BOTTOM | 0.25 | Margen inferior; no puede reducirse por debajo del 25 % |
| REEL_VOICE | es-DO-EmilioNeural | Voz española de Edge; no cambia de proveedor |
| REEL_MUSIC_PATH | sin valor | Archivo local requerido en music |
| REEL_MUSIC_VOLUME | 0.12 | Ganancia de música, admitida entre 0 y 0.3 |
| REEL_FFPROBE | detección por PATH | Ruta opcional a ffprobe |

Logo, texto, etiqueta y @ están todos en el área central. «Ejemplo ficticio» aparece dentro del teléfono; no hay barra fija de fuentes. Referencias FTC y NIST permanecen en caption.txt. El QR mantiene su etiqueta ilustrativa. El flag de borrador solo cambia el rótulo: no otorga aprobación editorial.

H.264, yuv420p de rango limitado, AAC cuando hay audio y MP4 faststart. El rango limitado se convierte explícitamente para evitar que las capturas JPEG produzcan yuvj420p. Sin escalado desde 540p. Se valida resolución, duración 17–21 s, fps, bitrate real de video >=4 Mbps, audio esperado, orden moov/mdat y decodificación de todo el archivo. Se usa ffprobe si existe; si no, FFmpeg/MoviePy ya incluidos. Un fallo no promociona el .partial.mp4 al archivo final.

La voz se mide por escena y se completa con silencio si sobra tiempo. Si dura más, se amplía la escena y se registra aviso, nunca se recorta ni se acelera. Si la duración total supera 21 s, el comando falla y hay que acortar la narración o revisar las duraciones en el JSON. Un fallo de Edge aborta: no usa Gemini ni devuelve un falso «reel con voz».

## Ejecución local

Desde la raíz del repositorio:

```powershell
.venv/Scripts/python.exe scripts/build_phishing_myth.py --render
$env:REEL_AUDIO="voice"
.venv/Scripts/python.exe scripts/build_phishing_myth.py --render
```

Salidas separadas por modo: `cyberpulse-bot/media/reels/phishing-myth-v3/none/`, `voice/`, `music/`. Cada una incluye preview.html, caption.txt, timing.json, escenas PNG, visual-checks.json, verification.json y reel-MODO.mp4 si la verificación termina bien. Los archivos generados no se versionan.

## Docker aislado, sin iniciar el bot

Docker está apagado en la máquina de revisión. No se ha ejecutado dentro de Docker ni se ha arrancado el stack de producción. Cuando Docker esté disponible, ejecutar desde `cyberpulse-bot/`. No usar `docker compose up` para esta prueba.

```powershell
docker build -t cyberpulse-reels:local .
docker run --rm --init --entrypoint python -e DRY_RUN=true -e PUBLICAR_EN_X=false -e REEL_AUDIO=none --mount "type=bind,source=$((Get-Location).Path)/media,target=/bot/media" cyberpulse-reels:local -m app.reels.myth --render
```

Para voz, usar el mismo comando sustituyendo `-e REEL_AUDIO=none` por `-e REEL_AUDIO=voice`. Requiere acceso de red a Edge TTS; no requiere .env ni credenciales de Meta/Gemini.

Para música, colocar un archivo propio/autorizado en `media/reels/musica-propia.wav`, sustituir el modo por `-e REEL_AUDIO=music` y agregar `-e REEL_MUSIC_PATH=/bot/media/reels/musica-propia.wav`. No se descarga música ni se distribuye una pista comercial.

Verificar una salida sin red ni render:

```powershell
docker run --rm --init --entrypoint python --mount "type=bind,source=$((Get-Location).Path)/media,target=/bot/media" cyberpulse-reels:local -m app.reels.check /bot/media/reels/phishing-myth-v3/none/reel-none.mp4 --audio none --duration 19
```

Estos comandos sobrescriben la entrada del contenedor y no cargan .env. El Dockerfile normal conserva su CMD de producción; nunca ejecutar esta imagen sin el override para una revisión.

## Pruebas y limitaciones reales

`cyberpulse-bot/tests/test_reel_myth.py`: ajustes, zonas, caption, voz completa sin recorte, rechazo de exceso de duración y música local de baja ganancia. `scripts/test_phishing_myth.py` conserva el acceso compatible, actualizado al contrato de 19 s y fallo cerrado de voz. Los tests del piloto anterior de contraseñas no cambian.

Render de integración opcional, sin servicio TTS: desde cyberpulse-bot, `REEL_EXPORT_TEST=1 python -m pytest tests/test_reel_myth.py -k native_voice` (en PowerShell establecer la variable antes). Usa tonos propios para simular la respuesta del proveedor y comprobar el montaje, no una narración real.

En la prueba de esta iteración, el catálogo de Edge confirmó es-DO-EmilioNeural, pero la síntesis fue rechazada con HTTP 403. No se afirma que la variante de voz real esté aceptada hasta conseguir una síntesis y escucharla. Un montaje de prueba con TTS simulado no acredita que el servicio externo funcione. La prueba de music usa un tono local propio, no una canción lista para publicar.

Resultados locales: 231 pruebas de backend pasan, una integración opt-in omitida en la suite normal; esa integración se ejecutó aparte y pasó. Las nueve pruebas de scripts también pasan. Ruff y diff sin errores. Exportaciones none y music: 1080×1920, 19 s, 24 fps, H.264 yuv420p, bitrate de video observado 4,948 Mbps y AAC en music. Verificación visual en 77 tiempos: área segura entre y=269 e y=1440, bucle con igualdad de frames y ventanas de movimiento inferiores a 1,5 s. Si se solicita el mínimo de 4 Mbps, el encoder usa objetivo mínimo de 4,1 Mbps para compensar el arranque del VBV; la aceptación exige medir al menos 4 Mbps reales.
