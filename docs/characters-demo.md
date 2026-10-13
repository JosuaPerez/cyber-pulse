# Prueba visual: plantilla y personajes

Muestra de doce segundos para revisar una nueva dirección visual. Abre con la
plantilla de CyberPulse y después amplía la escena con personajes SVG originales
frente a laptops. Muestra escritura de contraseña, exposición de la clave y un
intento de reutilizarla, conservando colores y tipografía. Al cerrar vuelve a la
plantilla principal. La muestra anterior con la metáfora de la llave permanece en
su directorio de medios generado.

Desde `cyberpulse-bot`:

```powershell
python -m app.demo_personajes
```

La vista previa está en `media/reels/characters-demo/preview.html`.
Permite reproducir, pausar y reiniciar la animación.

Para exportar una muestra con el fragmento WAV ya generado:

```powershell
python -m app.demo_personajes --export --duration 12 --audio media/reels/password-reuse-voice/narration.mp3 --subtitles media/reels/password-reuse-voice/subtitles.json --output media/reels/pace-demo
```

Requiere Chromium de Playwright. Produce `demo.mp4` de 540 × 960, 24 fps y doce
segundos, con H.264/AAC. Captura instantes deterministas de la animación y los envía
directamente a FFmpeg. La voz se reutiliza, sin llamadas a servicios ni costo de
síntesis. Con el comando mostrado se recortan los primeros doce segundos de la voz
aprobada y se usan sus marcas de subtítulos. El MP4 está en
`media/reels/pace-demo/demo.mp4`. Se admiten audios WAV o MP3 y `--duration` entre
uno y sesenta segundos. Sin marcas, se muestran textos explicativos de referencia.

Esta prueba permite evaluar personajes, cambios de plano y ritmo. Las cuentas se
seleccionan progresivamente, la cámara se acerca a la laptop y se abre para mostrar
el riesgo. La transición siguiente acompaña la entrada del ejemplo de la tienda.
La fase posterior requiere integrar los personajes en la línea de tiempo de las
seis escenas y revisar que la animación acompañe la voz y sus subtítulos.
No publica en Instagram ni modifica el generador del piloto anterior.

## Reel completo

```powershell
python -m app.demo_personajes --full --export --audio media/reels/password-reuse-voice/narration.mp3 --subtitles media/reels/password-reuse-voice/subtitles.json --voice-cache media/reels/password-reuse-voice/voice-cache --output media/reels/password-reuse-complete
```

El modo completo incorpora las seis partes del guion aprobado. Lee la duración de
cada WAV y añade la pausa de 0.35 segundos del montaje de voz. Comprueba que el MP3
coincida con esa duración y exige un único WAV por escena para evitar escoger una
voz equivocada. Esta animación está diseñada para el piloto de reutilización de
contraseñas; todavía no es un generador de historias arbitrarias.

Genera `reel.mp4`, `preview.html`, `timeline.json`, `caption.txt` y capturas de
control. Conserva el primer corte aprobado, continúa con la tienda y el atacante,
representa el correo y los enlaces de recuperación, y cierra con claves distintas,
gestor y verificación adicional. Los cambios de plano ilustran cada paso; no
representan un acceso exitoso garantizado ni protección infalible.

La salida de revisión usa 540 × 960 a 24 fps. Las versiones anteriores se conservan
en sus directorios. Se reutiliza audio y transcripción, sin nuevas peticiones de IA.
La voz, los subtítulos y el montaje deben revisarse juntos antes de publicar.
