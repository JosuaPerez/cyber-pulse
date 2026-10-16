# Laboratorio visual de alertas

Prueba aislada de cuatro diseños a 1080 × 1350. No reemplaza `PostInstagram`, no
cambia los datos del bot y no publica contenido. Todos los textos son ficticios
y las imágenes se identifican como demo editorial, no como alerta real.

Desde `cyberpulse-templates`, ejecuta `npm run dev -- --host 127.0.0.1`.

Abre estas rutas en el servidor local:

- `/?preview=alerts&variant=update`: actualización centrada en producto, versión y acción.
- `/?preview=alerts&variant=scam`: mensaje ficticio y señales de verificación.
- `/?preview=alerts&variant=context`: diagrama para explicar un concepto o noticia.
- `/?preview=alerts&variant=actions`: cierre práctico, con pasos y contexto de fuente.

Sin `preview=alerts`, el generador anterior funciona como antes. `variant` admite
solo las claves anteriores; cualquier otro valor usa `update`. No se aceptan
datos externos ni HTML desde parámetros para este laboratorio.

## Exportar y revisar

Con el servidor local activo y el entorno Python del proyecto con Playwright y
Pillow instalados, desde la raíz:

```powershell
.\.venv\Scripts\python.exe cyberpulse-templates/scripts/render-alert-preview.py
```

Las capturas, la comparación con la portada anterior y el contacto visual quedan
en `cyberpulse-bot/media/alert-preview/`, excluido de Git. La prueba bloquea
peticiones externas (incluida la foto remota de la portada anterior), espera las
fuentes locales y comprueba errores de página, dimensiones y desbordamiento.

## Antes de integrar al bot

Elegir dirección visual con el usuario. Después definir campos de producto y
versión, alcance confirmado, acción, fuente oficial y fecha. Separar urgencia de
tipo de noticia; no inferir severidad por el color de una plantilla. Si faltan
datos, indicarlo o mandar a revisión, nunca inventar versiones o confirmaciones.
Probar casos de títulos largos, campos ausentes y regresión de formatos existentes
antes de activar un nuevo renderizador en producción.

## Variante B para las alertas diarias

`DailyAlert` adapta la dirección B al contenido real de las cinco diapositivas:
resumen, problema, detalle técnico, riesgos y mitigaciones. No convierte noticias
arbitrarias en mensajes de phishing ni inventa remitentes, versiones o CVEs.
La severidad aparece como un dato separado del acento ámbar del diseño. La fuente
y el estado de explotación se toman de los metadatos ya preparados por el backend;
un dato ausente se indica como tal. No se infiere que una fuente sea oficial.

El generador sigue usando `clasica` por defecto. Para escoger B explícitamente:

```python
generar_imagenes_carrusel(datos_ia, variante_alerta="editorial")
```

No se activa en el ciclo diario todavía: el bot conserva su llamada original.
Educativos, tips, checklists y cheat sheets mantienen su diseño aunque se pase
esa opción. Una variante no reconocida produce un error antes de renderizar.
El frontend la recibe como `alertVariant=editorial` solo para `familia=alerta`.

Con el servidor de plantillas activo, desde `cyberpulse-bot`:

```powershell
python -X utf8 -m app.demo_alerta_editorial
python -X utf8 -m app.demo_alerta_editorial --stress --output media/alert-editorial-stress
```

La demo usa `content/alerts/editorial-demo.json`, identificado como ficticio;
no ejecuta el bot, llama a IA, sube imágenes ni publica. Sobrescribe el directorio
de imágenes solo dentro de ese proceso, sin tocar las imágenes del ciclo diario.
La variante B exporta cinco PNG y `carousel.png`; A (`--variant clara`) exporta
cuatro con detalle antes de las acciones de cierre, según `alerts-option-a.md`.
La prueba de límites comprueba longitudes
admitidas por el esquema. La variante rechaza desbordamientos en vez de devolver
imágenes recortadas. Antes de activarla, revisar noticias reales representativas
y la regresión del formato clásico.

## Carruseles completos A y C (solo laboratorio)

`AlertSeriesPreview` añade cinco diapositivas para cada propuesta. A representa
una actualización ficticia, con versión y alcance; C explica un incidente
hipotético, separando datos expuestos de acceso a cuentas. Todas las diapositivas
indican que son demos, sin noticias reales, versiones o CVEs inventados. La
severidad no está clasificada, porque no representan incidentes evaluados.

Rutas locales: `/?preview=alerts-series&variant=update&slide=1` y
`/?preview=alerts-series&variant=context&slide=1`; `slide` admite de 1 a 5.
Los valores desconocidos vuelven a la primera diapositiva o al ejemplo A.

Con el servidor activo, desde la raíz:

```powershell
.\.venv\Scripts\python.exe cyberpulse-templates/scripts/render-alert-series.py
```

Exporta en `cyberpulse-bot/media/alert-series/`, con cinco PNG y una comparación
por ejemplo. No conecta estas variantes A/C al generador diario. Los props
visuales adicionales de `DailyAlert` tienen valores predeterminados que conservan
la variante B; solo el laboratorio pasa los diseños y diagramas alternativos.
