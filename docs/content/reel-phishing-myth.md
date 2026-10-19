# Mito vs. mecanismo · «Si no doy clic, no pasa nada»

Guion aportado por Josua. Adaptación a voz en off e ilustración animada de teléfono.
Estado: borrador para revisión, no publicado ni programado. No reemplaza los archivos
de paquetería o el laboratorio de Git, que siguen disponibles por separado.

## Dos ajustes de precisión

- «Evita la mayoría de ataques» pasa a «reduce el riesgo»: no tenemos una fuente
  que cuantifique esa mayoría ni definimos un conjunto concreto de ataques.
- El QR representa el acceso a una web falsa y su petición, no una infección
  automática por apuntar la cámara. El escaneo por sí solo no prueba una infección.

No se atribuye una campaña, no se añaden víctimas ni cifras de alcance. Se habla de
engaños que pueden pedir distintas acciones, no de una garantía frente a todo ataque.

## Guion adaptado y tiempo objetivo

29 segundos estimados sin voz. Si se genera locución, las duraciones se miden en el
audio y el montaje las adopta, aunque el resultado salga del objetivo de 25–30 s.
No se acelera artificialmente una locución para ocultar que no encaja.

| Intervalo provisional | Voz | Visual |
| --- | --- | --- |
| 0–3 s | Si no das clic, ¿estás a salvo? Solo a medias. | Petición en el teléfono; cursor y pausa, sin pulsar el enlace. |
| 3–8 s | Evitar enlaces sospechosos reduce el riesgo. Pero no es la única puerta. | Se mantiene la pausa antes de actuar. |
| 8–11 s | También pueden engañarte con un archivo adjunto. | Un documento entra como alternativa al enlace. |
| 11–14 s | O pedirte datos por teléfono. | Icono de llamada y petición ficticia de datos. |
| 14–17 s | O llevarte a una web falsa desde un QR. | Esquema de QR sin destino; no se representa una infección instantánea. |
| 17–23 s | La regla es no actuar ante una petición sin verificarla por otro canal. | Salir del mensaje y abrir por cuenta propia la app oficial. |
| 23–29 s | Guárdalo. Si dudas, verifica por otro canal, no desde el mensaje. | Petición recibida → app oficial; cierre con invitación a guardar. |

El JSON `cyberpulse-bot/content/reels/phishing-myth.json` contiene narración,
titulares, fuentes y caption. No usa el renderer del primer reel de contraseñas.
La ilustración es original; no usa marcas reales, números de teléfono o enlaces activos.

## Respaldo editorial

- [FTC: reconocer phishing](https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams):
  enlaces y adjuntos como señuelos; comprobar solicitudes mediante un contacto conocido,
  no con los datos incluidos en el mensaje.
- [FTC: códigos QR](https://consumer.ftc.gov/consumer-alerts/2023/12/scammers-hide-harmful-links-qr-codes-steal-your-information):
  pueden dirigir a sitios falsos; recomienda verificar mediante canales conocidos.
- [NIST: phishing](https://www.nist.gov/itl/smallbusinesscyber/guidance-topic/phishing):
  incluye llamadas, además de mensajes y otras vías de contacto.

## Generar

```powershell
.venv\Scripts\python.exe scripts/build_phishing_myth.py --render
.venv\Scripts\python.exe scripts/build_phishing_myth.py --voice --render
.venv\Scripts\python.exe -m unittest discover -s scripts -p test_phishing_myth.py
```

`--voice` solicita Gemini TTS mediante la integración del proyecto y consume cuota.
En la prueba del 19/10/2026, el proveedor rechazó la narración con HTTP 429.
La entrega actual es por tanto un animatic SIN VOZ, no un reel narrado terminado.
No clona voces ni cambia de proveedor si falla. Reutiliza su caché cuando texto,
voz y ajustes coinciden. Un rechazo seguro del adaptador se anota en `timing.json`;
en ese caso se genera solo una vista sin voz identificada como tal. No se usa un
audio antiguo como si fuera la nueva locución.

Salida actual en `cyberpulse-bot/media/reels/phishing-myth-v2/`: vista HTML, storyboard,
caption, tiempos y MP4 de revisión 540×960 / 24 fps. Si hay voz, también WAV y MP4
con audio AAC. La vista HTML incorpora audio y fuentes para reproducirse sin servidor.
Los textos breves de pantalla son titulares, no una transcripción por palabra.

Revisar voz y duración, lectura móvil, transiciones, precisión y cierre antes de
exportar la entrega final 1080×1920. Nada se conecta al publicador del bot.

## Pulido visual v2

La carpeta `phishing-myth-v1` conserva el primer montaje para comparar.
El guion, las fuentes y los 29 segundos provisionales no cambian.

- Cursor cian situado bajo el enlace según su posición real; no cubre sus letras.
- Se retira «PAUSA», que podía confundirse con un botón de la interfaz.
- Entrada breve de titulares; teléfono con desplazamiento y acercamiento suaves;
  documento con micromovimiento; llamada con oscilación; barrido del QR dentro del
  icono y aparición escalonada de las tarjetas del cierre.
- Mensaje en superficie marino/cian con la misma familia tipográfica y bordes del
  resto de las tarjetas, sin el bloque claro de la v1.
- Disclaimer más contrastado y con fondo propio, separado al menos 24 píxeles
  del pie en la vista de revisión 540×960. El pie de marca queda en segundo plano.
- Se conserva el control «SIN VOZ · BORRADOR»: esta NO es la exportación final.
  Retirarlo solo en una entrega aprobada para publicación, con o sin voz; no retirar
  los disclaimers editoriales ni presentar tiempos estimados como sincronizados.

El renderer comprueba cursor/enlace y separación del pie cada 0,25 segundos;
también verifica cambios de movimiento dentro de cada escena y que volver al mismo
tiempo produzca el mismo estado. Guarda el resultado en `visual-checks.json`.
No se hace una nueva petición de voz durante este pulido; el límite 429 sigue pendiente.
