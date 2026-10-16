# Destacado «Empieza»

Tres historias de bienvenida, independientes del bot y sus alertas. Presentan la
promesa de CyberPulse, sus tres pilares y una forma práctica de aprovecharlos.
Las guías se identifican como una serie en construcción, no como recursos ya
disponibles. No incluyen estadísticas privadas ni noticias que puedan caducar.

## Exportar

Desde la raíz, con Playwright, Chromium y Pillow disponibles:

```powershell
.\.venv\Scripts\python.exe cyberpulse-templates/scripts/render-start-stories.py
```

Fuente editable: `cyberpulse-templates/content/stories-start.html`. Usa tipografía
local e iconos SVG propios; no requiere servidor, IA ni peticiones de red.
El exportador verifica fuente, errores, dimensiones y desbordamiento.

Salida ignorada por Git: `cyberpulse-bot/media/instagram-empieza/`.

- `historia-1.png`, `historia-2.png`, `historia-3.png`: 1080 × 1920, en ese orden.
- `portada-empieza.png`: 1080 × 1080; usar como portada, no como cuarta historia.
- `vista-previa.png`: contacto visual; no publicar esta composición.
- `cyberpulse-empieza.zip`: las tres historias y la portada, sin la composición.

## Publicación manual

1. Transferir los PNG originales al teléfono y guardarlos en Fotos.
2. Confirmar que se está usando @cyberpulse89.
3. Publicar las tres historias en orden en «Tu historia», no «Mejores amigos».
4. Abrir la primera historia y buscar «Destacar», posiblemente dentro de «Más».
5. Crear el destacado «Empieza» y añadir también las otras dos historias.
6. Editar la portada con `portada-empieza.png` y centrar el escudo.

Si la interfaz difiere, comprobar la pantalla real antes de seguir. No borrar las
historias para ocultarlas del feed: dejar que transcurran normalmente las 24 horas.
Revisar que el guardado en el archivo esté activado para futuras historias.

Este exportador no tiene acceso a Instagram ni publica. La publicación y su
visibilidad requieren comprobación en la cuenta; generar archivos no la confirma.
