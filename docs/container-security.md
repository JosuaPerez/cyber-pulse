# Seguridad de contenedores

CyberPulse separa el renderizador web y el bot en dos contenedores conectados por
una red interna de Docker Compose.

## Controles aplicados

- El frontend se compila con `npm ci` en una etapa separada. La imagen final no
  contiene `node_modules`, Vite ni las herramientas de compilación.
- El frontend se ejecuta como el usuario no privilegiado `node`, con el
  filesystem raíz de solo lectura, todas las capacidades Linux eliminadas y
  `no-new-privileges`.
- El puerto 5173 solo se expone a la red interna de Compose; no se publica en el
  host.
- El bot se ejecuta como el usuario no privilegiado `cyberpulse`, usa
  `no-new-privileges` y solo persiste datos en los volúmenes `data` y `media`.
- Ambos servicios usan un proceso `init` para recoger correctamente procesos
  hijos, especialmente Chromium.
- Las imágenes base están fijadas por digest y Dependabot propone sus
  actualizaciones mensualmente mediante pull requests.
- Los contextos de construcción excluyen secretos, entornos virtuales, datos,
  medios, cachés y artefactos locales.
- Las dependencias directas de AWS y sus componentes de resolución quedan
  fijadas a versiones exactas.

## Operación

Desde `cyberpulse-bot/`:

```bash
docker compose build
docker compose up -d
docker compose ps
```

El frontend no debe abrirse mediante `localhost:5173`: es un servicio interno
consumido por Playwright desde `http://plantillas-vite:5173`.

Para comprobar la configuración sin mostrar las variables resueltas del entorno:

```bash
docker compose config --quiet
```

Evita compartir la salida completa de `docker compose config`, porque Compose
puede interpolar secretos procedentes de `.env`.

## Riesgo residual de compilación

`npm audit --omit=dev` no reporta vulnerabilidades en el runtime. Tailwind CSS 3
mantiene dependencias de compilación con avisos de denegación de servicio; esas
dependencias no se copian a la imagen final. Eliminarlas exige migrar a Tailwind
CSS 4 y validar visualmente todas las plantillas, por lo que se trata como una
refactorización independiente y no se aplica con `npm audit fix --force`.

## Rollback

Si el renderizador deja de responder tras una actualización, revierte el commit
del cambio y reconstruye solo el servicio afectado:

```bash
docker compose build plantillas-vite
docker compose up -d --no-deps plantillas-vite
```
