# Alertas nuevas: contrato único de cuatro diapositivas

El analizador RSS usa `AnalisisAlerta` para todas las noticias nuevas. Gemini
entrega una sola redacción tipada, sin duplicar `slide_1..slide_5` y `editorial`.
El código deriva el carrusel, caption y hilo de ese resultado. `AnalisisIA`
continúa disponible para educativos y sus formatos de cinco imágenes.

## Contrato y render

Los límites se definen en `app/limites.py` y alimentan esquema y prompt.

| Tarjeta | Campos principales |
| --- | --- |
| `card_lo_esencial` | `portada_titulo`, `resumen_hallazgo`, `nota_vigencia` |
| `card_te_afecta` | `hecho_documentado`, `a_quien_concierne`, `audiencia` |
| `card_contexto` | `detalle_analisis`, `lo_que_no_podemos_concluir`, CVEs |
| `card_que_hacer` | 2–3 acciones con rol y CTA fijo |

Las noticias con `editorial_version=3` siempre generan cuatro imágenes, incluso
si la configuración conserva `ALERTAS_VARIANTE=clasica`. Los formatos guardados
anteriores conservan su render explícito para revisión, pero el centinela exige
un paquete nuevo validado antes de renderizar y publicar.

Se mantiene el marco específico de riesgos operativos: personas, herramientas
y políticas. La nota de vigencia validada se muestra sin sustituir explotación
histórica confirmada por una frase genérica que niegue ataques.

## Evidencia y rechazos

- Nombre del fallo y boletín: copia literal o campo vacío. No convertir una
  descripción como «RCE en Drupal» en un apodo inventado.
- `evidencia_identidad` es una lista de citas/IDs independientes. Cada CVE debe
  estar asociado al nombre y boletín declarados en su cita. La mera presencia
  de identificadores distintos en un mismo artículo no prueba su relación.
- Se resuelven IDs `FUENTE_001` del catálogo antes de comprobar citas literales.
  No se traducen, recortan ni reparan citas fallidas.
- Se comprueban CVEs, boletines, hotfix, versiones y CVSS en todos los textos
  públicos, incluido caption y acciones. Los hotfix de una acción deben aparecer
  también en la evidencia de esa acción.
- Explotación activa exige evidencia afirmativa. Una negación de ataques en
  cualquier tarjeta/caption contradice ese estado y provoca rechazo. El silencio
  de una fuente corresponde a estado desconocido, no a ausencia confirmada.
- La prioridad crítica necesita explotación confirmada o una referencia
  explícita a ejecución remota sin autenticación. La prioridad editorial es
  conservadora; puede ser inferior a la etiqueta del fabricante cuando el
  extractor no ofrece respaldo suficiente para esa comprobación.
- Las acciones específicas necesitan una recomendación literal del mismo
  control. Se admiten familias conocidas: actualización, copias, multifactor,
  ayuda especializada, políticas, formación, herramientas aprobadas, retención,
  rotación de claves y desinstalación. Otros controles requieren revisión.
- Máximo una consulta general, al menos una medida concreta y ningún relleno
  con consultas repetidas. Una acción inválida no se sustituye por texto genérico.
- Frases duplicadas entre tarjetas y jerga técnica no apta para el carrusel
  provocan rechazo.

Gemini recibe el motivo y el borrador rechazado para corregir la respuesta
completa. Tras tres intentos fallidos no se devuelve un paquete publicable.
La API recibe `response_json_schema`; la validación local mantiene
`extra="forbid"`. Esto evita el rechazo de `additional_properties` que producía
la conversión del esquema anterior en esta integración de Gemini.

Estas comprobaciones reducen errores concretos; no prueban toda la semántica de
una noticia ni detectan exhaustivamente nombres inventados en prosa libre.
No sustituyen el contraste editorial con la fuente primaria. Se conserva la
primera etapa de revisión antes de activar publicación autónoma.

## Prueba real sin publicar

Desde `cyberpulse-bot`, con Docker abierto:

```powershell
docker compose -p cyberpulse-review build
docker compose -p cyberpulse-review up -d plantillas-vite
docker compose -p cyberpulse-review run --rm --no-deps -e DRY_RUN=true -e PUBLICAR_EN_X=false bot-python python -m app.revisar_alerta --url URL_HTTPS --title "Título real"
```

El proyecto Docker `cyberpulse-review` mantiene sus plantillas separadas del
centinela en ejecución. Esta orden llama a Gemini, descarga la fuente y exporta
cuatro PNG 1080×1350, `carousel.png`, `analisis.json` e `intentos.json` bajo
`media/revision-alertas/`. El registro incluye la fuente analizada, los borradores
y los rechazos; no incluye credenciales. No lee/reserva noticias del historial,
no sube archivos a R2 y no llama a Instagram ni X.

Los medios y registros generados están excluidos de Git. La muestra de Drupal
del 18 de octubre de 2026 se generó con Gemini después de rechazar una afirmación
de ausencia de ataques sin respaldo y una prioridad crítica sin evidencia
suficiente para el filtro. Se revisaron versiones y medidas frente a:

- https://www.drupal.org/sa-core-2026-014
- https://www.drupal.org/sa-contrib-2026-218

## Integración y puesta en marcha

Revisar y fusionar el PR de migración completo; no hace falta fusionar por
separado la rama de respaldo. Después, actualizar el checkout de producción y
reconstruir ambos servicios con `docker compose up -d --build`.

Mantener `DRY_RUN=true` durante la primera revisión. El centinela guarda el
análisis, caption e imágenes y marca esa noticia como revisión manual en SQLite.
Cambiar a `DRY_RUN=false` solo al concluir esa etapa y recrear `bot-python` para
que reciba el valor nuevo. Ese cambio publica las noticias nuevas que reserve
RSS; no aprueba ni republica automáticamente las ya marcadas para revisión.
No borrar el historial para forzar una publicación: protege frente a duplicados
y resultados ambiguos de Meta.

Las revisiones JSON antiguas son ediciones manuales, no fixtures de rechazo ni
validaciones automáticas. Su exportador elimina el sello v3 y los identificadores
heredados del análisis base. El centinela rechaza esos paquetes manuales.

## Pruebas

Desde `cyberpulse-bot`: `..\.venv\Scripts\python.exe -m pytest -q` y
`..\.venv\Scripts\ruff.exe check app tests`. Desde `cyberpulse-templates`:
`npm.cmd run lint`, `npm.cmd test`, `npm.cmd run build`.

La regresión cubre identificadores inventados, relaciones equivocadas entre
CVEs, explotación contradictoria, evidencia negada, acciones sin respaldo,
desinstalación condicional, límites, reintentos, fallo de API, bloqueo de datos
alterados/legacy y publicación simulada exclusivamente con cuatro imágenes.
Los tests antiguos de salida duplicada se migraron a ese contrato; se mantienen
las pruebas del esquema educativo y del render legacy.
