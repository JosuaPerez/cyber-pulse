# Reel Mito vs. mecanismo · versión 4 (segunda ronda)

Estado: implementado para revisión local, no publicado ni programado. La primera ronda se guardó en el commit 334bb34. El guion tiene seis escenas: 19 s sin audio y aproximadamente 20,9 s con voz real, sin acelerar ni recortar palabras.

## Arquitectura real y alcance

Este piloto usa HTML autónomo + Playwright, no React/Vite. Se conserva esa arquitectura, sin modificar alertas, carruseles, feed, proveedores compartidos, Dockerfile de producción ni compose. Se añade Dockerfile.reels, una imagen aislada con Edge TTS 7.3.1 y ffprobe. El script de construcción sigue delegando a módulos pequeños en `cyberpulse-bot/app/reels/`:

- `settings.py`: constantes 1080×1920, JSON, flags, márgenes y numeración derivada del orden de trampas; URL ficticia limitada a .invalid.
- `audio.py`: MoviePy para silencio/mezcla, Edge TTS por escena mediante el adaptador existente. Timeout total de voz: 120 s.
- `preview.py`: HTML autónomo, fuentes locales, caption, portada y comprobación de píxeles cada 0,5 s, sin contar pie ni barra de progreso.
- `render.py`: capturas nativas a escala 1, codificación FFmpeg y verificación completa.
- `myth.py`: CLI y comparación none/voice en un comando, sin importaciones del publicador.
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
| 16–19 | Guárdalo; pregunta y opciones 1–3 |

Entradas con easing de 0,25 s y cortes entre escenas; zoom del fondo del 4 %. El archivo se abre y revela un permiso de macros, la llamada tiene ondas y burbuja, y el QR revela una URL ficticia no navegable. El teléfono mide 720×610 frente a 536×468 anteriores (aproximadamente 1,34×/1,30×); los textos secundarios y el aviso del teléfono tienen al menos 44 px. El bloque principal está centrado dentro de la zona segura con 64 px laterales.

La solución muestra tarjeta, check y después la instrucción. El cierre incorpora marcador, burbuja y seguimiento de la serie. El SMS no tiene número: las tres trampas derivan 1–3 del orden de la lista, también en tarjetas, progreso, cierre y pregunta. No editar números en la plantilla.

Los últimos 0,18 s funden con una copia del estado inicial, preparada después de cargar las fuentes para no desplazar el cursor. El último frame exportado es idéntico al primero. El bucle es visual, sin recortar el audio.

Referencia visual: MP4 proporcionado por Josua correspondiente al reel De4MLZghFbW, de 2:51. Se revisaron fotogramas de todo el video y con más frecuencia la apertura. Se toma la progresión de elementos, diagramas distintos y jerarquía tipográfica como orientación; no se copian texto, datos, música ni afirmaciones sobre XKeyscore.

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
.venv/Scripts/python.exe scripts/build_phishing_myth.py --compare --render
```

Salidas separadas por modo: `cyberpulse-bot/media/reels/phishing-myth-v4/none/`, `voice/`, `music/`. Cada una incluye cover.png 1080×1920, preview.html, caption.txt, timing.json, escenas PNG, visual-checks.json, verification.json y reel-MODO.mp4 si la verificación termina bien. --compare genera none y voice secuencialmente, copia la portada a la carpeta base y escribe comparison.json completo solo si ambas terminan. Los archivos generados no se versionan. Para ejecución local con voz se necesita el runtime aislado de app/reels/requirements.txt; no actualizar las dependencias del bot por esta prueba.

## Docker aislado, sin iniciar el bot

Docker está apagado en la máquina de revisión. No se ha ejecutado dentro de Docker ni se ha arrancado el stack de producción. Cuando Docker esté disponible, ejecutar desde `cyberpulse-bot/`. No usar `docker compose up` para esta prueba.

```powershell
docker build -f Dockerfile.reels -t cyberpulse-reels:local .
docker run --rm --init -e DRY_RUN=true -e PUBLICAR_EN_X=false --mount "type=bind,source=$((Get-Location).Path)/media,target=/bot/media" cyberpulse-reels:local --compare --render
```

Una vez construida la imagen, la segunda línea es el único comando que regenera portada y ambas versiones. Usa red para Edge TTS, pero no .env ni credenciales de Meta/Gemini. Para un modo aislado, omitir --compare y pasar -e REEL_AUDIO=none o voice antes del nombre de la imagen.

Para música, colocar un archivo propio/autorizado en `media/reels/musica-propia.wav`, omitir --compare y pasar -e REEL_AUDIO=music y -e REEL_MUSIC_PATH=/bot/media/reels/musica-propia.wav antes de la imagen; conservar --render. No se descarga música ni se distribuye una pista comercial.

Verificar una salida sin red ni render:

```powershell
docker run --rm --init --entrypoint python --mount "type=bind,source=$((Get-Location).Path)/media,target=/bot/media" cyberpulse-reels:local -m app.reels.check /bot/media/reels/phishing-myth-v4/none/reel-none.mp4 --audio none --duration 19
```

La imagen Dockerfile.reels arranca únicamente el módulo de reels, también sin override. El Dockerfile normal del bot no cambia. No confundir las dos imágenes ni usar compose de producción para esta revisión.

## Pruebas y limitaciones reales

`cyberpulse-bot/tests/test_reel_myth.py`: ajustes, zonas, caption, voz completa sin recorte, rechazo de exceso de duración y música local de baja ganancia. `scripts/test_phishing_myth.py` conserva el acceso compatible, actualizado al contrato de 19 s y fallo cerrado de voz. Los tests del piloto anterior de contraseñas no cambian.

Render de integración opcional, sin servicio TTS: desde cyberpulse-bot, `REEL_EXPORT_TEST=1 python -m pytest tests/test_reel_myth.py -k native_voice` (en PowerShell establecer la variable antes). Usa tonos propios para simular la respuesta del proveedor y comprobar el montaje, no una narración real.

La primera ronda con Edge TTS 7.2.8 fallaba con HTTP 403. Se verificó la corrección oficial Sec-MS-GEC v2 (https://github.com/rany2/edge-tts/pull/492) y se probó 7.3.1 en una carpeta aislada; esa versión también queda fijada en la imagen de reels. La síntesis real con es-DO-EmilioNeural funciona. La primera locución completa excedía 21 s; se abreviaron gancho, QR y cierre para mantener la voz a velocidad normal y la explicación completa en pantalla. La salida narrada dura aproximadamente 20,9 s. No se sustituye ninguna voz por tonos ni se cambia de proveedor.

Resultados locales de segunda ronda: 234 pruebas de backend pasan, una integración opt-in omitida en la suite normal; nueve pruebas de scripts pasan. Salidas reales none/voice: 1080×1920, 19/~20,9 s, 24 fps, H.264 yuv420p, aproximadamente 5 Mbps y AAC en voice. Se comparan píxeles cada 0,5 s, excluyendo pie y progreso; no se detectan intervalos inmóviles de 1,5 s. Se conservan la verificación de decodificación, faststart y área segura. La voz real también se escucha antes de aprobar la publicación: validación técnica no es aprobación editorial ni garantía de calidad subjetiva. Docker sigue apagado; no se afirma ejecución dentro del contenedor.
