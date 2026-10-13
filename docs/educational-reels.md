# Reels educativos: piloto v1

Serie: **Conceptos en claro**, de CyberPulse (@cyberpulse89).
Audiencia: personas que empiezan a aprender ciberseguridad.

El piloto explica la reutilización de contraseñas con un ejemplo ficticio. Sigue seis
escenas: gancho, filtración, credential stuffing, riesgo del correo, protección y
una acción final. El guion editorial está en
`cyberpulse-bot/content/reels/password-reuse.json` y debe revisarse antes de publicar.
Incluye caption y enlace de referencia. La existencia de un enlace no sustituye la
verificación de las afirmaciones de cada guion.

## Vista previa

Desde `cyberpulse-bot`, con las dependencias del proyecto instaladas:

```powershell
python -m app.reel_educativo
```

Abre `media/reels/password-reuse/preview.html`. Los controles permiten reproducir,
pausar y reiniciar. La vista sin audio usa una estimación de lectura; lo indica en
pantalla. No necesita CDN, claves de API ni llamadas a Gemini.

## Exportar

Instala Chromium para Playwright si aún no está disponible:

```powershell
python -m playwright install chromium
python -m app.reel_educativo --export
```

El guion de cada escena se envía al servicio usado por `edge-tts` para producir voz
en español colombiano (`es-CO-GonzaloNeural`). Se puede seleccionar otra voz con
`--voice`. La duración real de cada fragmento determina cuándo cambia la escena.
El servicio puede rechazar solicitudes (por ejemplo, HTTP 403); no hay voz de
respaldo silenciosa ni se presenta una estimación como narración terminada.

### Voz con Gemini

Para usar la alternativa probada con la configuración existente del proyecto:

```powershell
python -m app.reel_educativo --audio-only --provider gemini --output media/reels/password-reuse-voice
python -m app.reel_educativo --export --provider gemini --width 540 --output media/reels/password-reuse-voice
```

Requiere `GEMINI_API_KEY`, cargada desde `cyberpulse-bot/.env` o el entorno.
Usa explícitamente Gemini 3.8 Flash-Lite TTS y la voz de estudio Charon; no clona la
voz de ninguna persona. Se puede cambiar con `--tts-model` y `--voice`. La petición
REST mantiene el texto separado de las instrucciones de lectura y usa `store=false`.
Referencia: https://ai.google.dev/gemini-api/docs/speech-generation

La generación consume la cuota y, según el plan, puede tener costo. No hay cambio
automático de proveedor ni reintentos ante cuota agotada. La caché `voice-cache/`
identifica texto, proveedor, voz, modelo y estilo: si no cambian, el render reutiliza
el audio y no pide otra síntesis. Los cambios de voz o guion generan una entrada
nueva. Los archivos antiguos permanecen disponibles para comparar.

`--audio-only` permite escuchar las escenas antes de renderizar. La exportación con
voz guarda además `narration.mp3`, con pausas de 0.35 segundos entre escenas, y la
incrusta en la vista previa. El diseño conserva los tiempos medidos del audio real.
El directorio de salida distinto conserva la muestra visual anterior.

### Subtítulos sincronizados

```powershell
python -m app.reel_educativo --export --provider gemini --subtitles --width 540 --output media/reels/password-reuse-voice
```

Reutiliza las seis voces de `voice-cache/`. Gemini 3.5 Transcribe analiza el audio
completo y devuelve marcas de inicio y fin por palabra. La transcripción consume
cuota de Gemini; sus marcas se guardan por hash del audio y modelo. El sistema
rechaza marcas desordenadas, solapadas o fuera del audio, así como una transcripción
que difiera sustancialmente del guion. No se sustituyen marcas fallidas por tiempos
calculados a partir de la longitud del texto.

Los bloques tienen hasta cinco palabras y se separan en pausas y cambios de escena.
La vista previa y el MP4 usan las mismas marcas; la palabra actual cambia al color
de la escena. El MP4 incorpora la capa de subtítulos separada del zoom del fondo.
Se crean `reel-subtitled.mp4`, `preview-subtitled.html`, `subtitles.json` y
`subtitles.srt`; se conservan el reel y la vista previa anteriores. El SRT permite
revisar las frases y reutilizarlas en un editor, pero no contiene el resaltado por
palabra. Las marcas automáticas requieren una revisión audiovisual antes de publicar.

Referencia: https://ai.google.dev/gemini-api/docs/transcribe

Para revisar el diseño sin depender del proveedor:

```powershell
python -m app.reel_educativo --export --silent --width 540
```

Esto produce un **borrador sin voz**, con tiempos estimados. La exportación normal
es de 1080 × 1920, 24 fps, H.264/AAC, píxeles yuv420p y faststart. La muestra de
540 × 960 acelera la revisión; usa 1080 para la versión de publicación.

Se generan `reel.mp4`, `preview.html` y `caption.txt` dentro de `media/reels/<id>/`.
Los medios están ignorados por Git; el guion, plantilla y generador sí se versionan.
Volver a exportar el mismo ID reemplaza los artefactos anteriores.

## Alcance visual y revisión editorial

La v1 usa tarjetas e interfaces esquemáticas, texto de apoyo por escena, acentos
cian/ámbar/violeta y movimiento suave de cámara. El MP4 utiliza capturas de cada
escena con zoom ligero y entrada breve; no reproduce toda la interacción HTML.
Sin `--subtitles`, el texto inferior muestra el fragmento completo de narración.
Con esa opción, cambia a bloques breves con resaltado sincronizado por palabra.
Las siguientes iteraciones pueden añadir diagramas animados.

Revisar antes de publicar:

- Concepto correcto, sin presentar multifactor como protección infalible.
- Lenguaje entendible por principiantes; explicar anglicismos al introducirlos.
- Texto legible en móvil y libre de controles superpuestos de Instagram.
- Pronunciación, pausas y duración de la voz aprobadas.
- Identidad CyberPulse propia y recursos visuales originales.

La herramienta no publica ni se conecta a Meta. Permite probar el formato antes de
integrarlo con el calendario, el análisis IA y la aprobación del bot educativo.

## Pruebas

```powershell
python -m ruff check app tests
python -m pytest -q
```

Si la carpeta `.pytest-tmp` tiene permisos inválidos en Windows, se puede evitar la
ruta fija para una ejecución local:

```powershell
python -m pytest -q -o "addopts=-p no:cacheprovider"
```

Las pruebas del piloto verifican validación del guion, duración por escena y que
el texto no pueda cerrar el elemento HTML `script`.
