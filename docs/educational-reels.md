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
El texto inferior muestra el fragmento completo de narración: todavía no son
subtítulos palabra por palabra. Las siguientes iteraciones pueden añadir diagramas
animados, marcas temporales de voz y subtítulos más breves.

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
