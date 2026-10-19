# CyberPulse Lab · animatic en movimiento / v2

Primer prototipo animado, sin voz, pendiente de revisión. No publicado ni programado.
Se conserva el montaje v1 de cinco imágenes para comparar.

## Qué cambia

- La línea de la credencial ficticia se tacha y sale del archivo.
- Un marcador recorre dos commits; la tarjeta cambia de versión durante el recorrido.
- La revisión anterior vuelve a mostrar el valor que realmente conservó Git.
- La medida «revocar o rotar si hubo exposición real» entra como un paso separado.
- El MP4 se renderiza a 24 fotogramas por segundo desde una función del tiempo;
  no es un montaje de una captura fija por escena.

El repositorio sigue siendo temporal, propio y sin remotos. El generador reutiliza
la demostración de dos commits de `build_git_history_lab.py`. La animación es una
representación explicativa de esos datos, no una grabación continua de una terminal.

## Revisar

```powershell
.venv\Scripts\python.exe scripts/build_git_history_motion.py --render
```

Para exportar solo los primeros seis segundos, añadir `--opening-only`.
La vista HTML es interactiva y no necesita APIs ni paquetes adicionales.

Salida: `cyberpulse-bot/media/labs/git-history-motion-v2/`.
Contiene `preview.html`, `lab-motion-sin-voz.mp4`, muestras PNG, una tira de revisión,
los datos de la prueba y un registro de validación del render.

La duración provisional es de 29 segundos. No hay audio ni subtítulos pretendidamente
sincronizados. Tras revisar el lenguaje visual, generar o recibir la locución,
medir sus tiempos y asociar eventos a las palabras pertinentes; no acelerar la voz
solo para ajustarla a esta estimación. Después, añadir subtítulos y exportar a 1080×1920.

Los cambios no afectan alertas, bot, credenciales, proveedor ni programación.
