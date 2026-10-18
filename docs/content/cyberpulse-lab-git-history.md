# CyberPulse Lab / 001 · Borraste la clave. ¿Y el historial?

Estado: guion y primer montaje SIN VOZ para revisión. No publicado ni programado.
Serie adicional a las alertas y a «Conceptos en claro», no reemplaza la paquetería.
Duración de montaje: 27 s; la voz final puede requerir ajustar estos tiempos.

## Qué se demuestra realmente

El generador crea un repositorio nuevo en una carpeta temporal del sistema,
sin remotos, sin hooks de usuario y con identidad de prueba. Hace dos commits:

1. `app.ini` contiene `API_TOKEN=DEMO_ONLY_NOT_VALID_001`.
2. La versión siguiente ya no contiene esa línea.

Ejecuta de verdad `git show HEAD:app.ini` y `git show HEAD~1:app.ini`.
El montaje utiliza sus resultados, no salidas de terminal inventadas. Se verifica
que el valor esté ausente en HEAD y presente en su padre. Se conserva evidencia
JSON con los identificadores de los commits, no el repositorio temporal.

No se lee el `.env` de CyberPulse, no se abre un servidor, no se consulta GitHub
ni se examinan repositorios ajenos. No se reescribe el historial de este proyecto.
La credencial de prueba es una cadena inválida sin acceso a servicio alguno.

## Guion de montaje

| Tiempo | Pantalla | Enseñanza |
| --- | --- | --- |
| 0–4 s | «Borraste la clave. ¿Y el historial?» + comparación de ambas revisiones | Mostrar el resultado desde la apertura. |
| 4–10 s | Versión actual sin la credencial | Diferenciar archivo actual e historial. |
| 10–16 s | Commit anterior, valor ficticio resaltado | Mostrar la persistencia en una revisión accesible. |
| 16–24 s | «Revoca o rota. Borrar no basta.» | Remediación si una credencial real quedó expuesta. |
| 24–27 s | Revisión antes del commit + guardar | Una acción de prevención. |

Narración y caption editables: `cyberpulse-bot/content/labs/git-history.json`.
No se copiaron el vídeo, voz, identidad ni recursos del creador de referencia.
El primer montaje usa cortes entre cinco escenas, sin captura continua de terminal
ni audio: es una revisión de contenido y lectura, no un reel final con voz.
No se imprime la locución completa sobre el vídeo: se evita duplicar el texto.
La narración propuesta está en el JSON; los subtítulos sincronizados quedan pendientes.

## Fuentes y condiciones

[GitHub: retirar información sensible](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
explica que, ante un secreto expuesto, debe revocarse o rotarse y que limpiar
historiales tiene efectos sobre colaboradores y copias. Por eso no ofrecemos
reescribir el historial como arreglo automático ni como sustituto de invalidar la clave.

La demostración no prueba acceso externo ni una filtración real. Tener historial
local no equivale a que cualquier persona pueda leerlo: requiere acceso a esa copia.
Usar variables de entorno no borra secretos que ya se hayan versionado.

## Generar y verificar

Desde la raíz, sin TTS ni consumo de cuota:

```powershell
.venv\Scripts\python.exe -m unittest discover -s scripts -p test_git_history_lab.py
.venv\Scripts\python.exe scripts/build_git_history_lab.py --render
```

Archivos generados en `cyberpulse-bot/media/labs/git-history-v1/` (ignorados por Git):

- `preview.html`: vista interactiva autónoma con fuentes incluidas.
- `lab-sin-voz.mp4`: 540×960, 24 fps, H.264, 27 segundos sin audio.
- `scene-1.png` a `scene-5.png`: láminas de revisión 1080×1920.
- `storyboard.png`, `caption.txt`, `evidence.json`.

La ejecución regenera esta carpeta de salida; no sustituye las muestras de paquetería.

## Antes de publicar

Revisar apertura, legibilidad móvil y precisión. Tras aprobar el guion, producir
voz original, ajustar duración a la locución y sincronizar subtítulos; luego
exportar 1080×1920 y revisar principio, transiciones, cierre y zonas de interfaz.
No está conectado al publicador automático del bot. La fecha se acuerda después
de esa revisión; el calendario de paquetería no se altera automáticamente.
