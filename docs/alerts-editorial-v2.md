# Alertas claras · contrato visual y editorial común (v2)

Esta capa sustituye la ficha especial de máquinas virtuales para nuevas alertas.
Se aplica a TODAS las noticias que analiza el bot con `ALERTAS_VARIANTE=clara`, no
a una lista de nombres, CVEs, fabricantes o medios. Reels, cheat sheets y el
formato clásico no cambian. No activa publicación pública ni cambia el `.env`.

## Contrato

`AnalisisIA.editorial` conserva compatibilidad con datos anteriores, pero el
analizador exige su presencia para producir nuevas alertas claras. Si falta o
no supera las comprobaciones, reintenta; agotados los intentos, falla sin publicar.
El formato anterior permanece disponible para muestras congeladas explícitas y
rollback. No se usa silenciosamente como reemplazo de un análisis nuevo fallido.

Los cuatro slides leen la misma ficha tipada:

1. Gancho y resumen accesibles, con un visual.
2. `hecho` documentado separado de `alcance` potencial y audiencia (general,
   administradores o mixta). No confundir víctimas documentadas con todos los lectores.
3. Explicación comprensible y lo que no puede concluirse para un equipo concreto.
4. Dos o tres acciones, etiquetadas «Para ti» o «Para equipos de TI», y CTA.

La ficha contiene evidencias literales, un caption breve y acciones con rol,
texto, evidencia y distinción entre medida específica y orientación general.
Esta última solo admite verbos de consulta o comprobación; no sirve para pasar
un bloqueo o instalación como recomendación respaldada. Las medidas específicas
requieren una cita de la fuente. Se rechazan hashes, varios formatos de indicadores
de red y jerga/instrucciones de registros en los campos visibles. No es un detector
exhaustivo de entidades ni una garantía de legibilidad o veracidad semántica.

El código ofrece al modelo fragmentos numerados `FUENTE_001`, etc. Los IDs se
resuelven al texto original antes de verificarlo; un ID desconocido no acredita
una afirmación. Sigue siendo necesario revisar que la cita respalde el significado,
no solo que exista. Si una acción marcada como orientación general intenta dar
una instrucción operativa, se sustituye por una consulta prudente según el rol y
se registra en `meta.ajustes_editoriales` para revisión. Una medida marcada como
específica no se aprueba por esta vía: sin evidencia se rechaza.

La normalización incluye un glosario reducido (por ejemplo, «payload» → «código
entregado»). Un detalle dominado por indicadores se remite al informe y usa el
resumen factual ya aportado, no una explicación inventada. Las tareas de registros
y aplicación de indicadores se convierten en consulta con el equipo de seguridad,
no en una supuesta regla de detección simplificada. Estos ajustes quedan registrados.
Se revalida el resultado; si la expansión de lenguaje supera límites no se recorta
silenciosamente: se rechaza y reintenta. Esta vía puede producir piezas menos
específicas: revisar su utilidad antes de publicar, no confundir seguridad con calidad.
Las acciones para personas se muestran antes de las de administración. Un caption
que pida tareas operativas de red se sustituye por el resumen, el límite y una
pregunta accesible, conservando un registro del ajuste.

## Visuales sin excepciones por noticia

- `cadena`: dos o tres etapas. Cada nodo y su relación deben tener evidencia
  literal presente en el texto. Es una ilustración, no una regla de detección.
- `comparacion`: dos o tres elementos documentados con evidencia de su relación.
- `resumen`: mapa neutral «lo reportado por la fuente ≠ tu dispositivo», cuando
  falta respaldo para una secuencia específica. No representa un ataque inventado.

Una selección visual incompleta o sin evidencia cae en el mapa neutral; no se
publica una secuencia plausible inventada. El frontend acepta solo tipos conocidos,
limita nodos/textos y renderiza las etiquetas como texto React, nunca HTML.
Comprobar citas no demuestra que un diagrama describa correctamente el caso:
relación, negaciones y matices siguen requiriendo revisión editorial.

## Tiempo y referencias

La fecha de preparación UTC sigue siendo distinta del periodo de los hechos.
`historica` requiere una cita temporal; el otro estado es `vigencia_no_confirmada`.
Ninguno de los dos afirma una campaña activa ahora solo porque el informe sea nuevo.
El estado de explotación bruto permanece en el registro, no se convierte en una
aseveración de vigencia en la portada v2.

Los indicadores y el análisis técnico original se conservan en el JSON, sin hashes
largos en el carrusel. En DRY_RUN se guardan `analisis_pendiente.json` y
`referencia_tecnica.txt`, además del caption y las rutas de los PNG en
`post_pendiente.txt`. Son archivos locales excluidos de Git, no una página pública
de recursos. El caption incluye la URL del informe; no se promete un recurso
externo que no exista. El hilo de X usa el mismo gancho, resumen y acción accesible.
El borrador editorial original y los ajustes se conservan en metadatos para no
ocultar sustituciones. La prioridad editorial crítica se limita a alta si no hay
explotación activa reportada ni una referencia textual a RCE sin autenticación.
Esta comprobación no valida todas las condiciones de explotación ni equivale a
la calificación CVSS de un proveedor; revisar la prioridad antes de publicar.

## Verificación

Con el servidor de plantillas activo, desde `cyberpulse-bot`:

```powershell
python -X utf8 -m app.demo_editorial_universal
python -X utf8 -m app.demo_editorial_universal --stress
```

Son demostraciones ficticias de resumen, comparación y cadena, con cuatro PNG por
caso y prueba de desbordamiento. Exportan bajo `media/editorial-universal/`.
No consumen IA ni llaman a redes sociales. Las pruebas unitarias incluyen noticias
sin categoría específica, evidencia ausente, medidas por rol, fechas, indicadores,
selección visual y compatibilidad con el formato clásico.

`python -X utf8 -m app.revisar_alerta --url <artículo-HTTPS-permitido> --title <título>`
prueba la ficha con un artículo real y Gemini; consume cuota, no consulta el
historial y no publica. Revisar el resultado, no solo que haya cuatro imágenes.

Mantener DRY_RUN hasta revisar varias noticias de clases diferentes. El contrato
no evita todas las alucinaciones y puede rechazar respuestas; fallar y pedir
revisión es preferible a declarar todo el contenido automáticamente publicable.

## Exportación manual revisada

Una revisión humana se guarda como datos en `cyberpulse-bot/content/alerts/reviews/`;
no agrega excepciones por noticia al generador automático. Con las plantillas
activas, desde `cyberpulse-bot`:

```powershell
python -X utf8 -m app.exportar_alerta_revisada --analysis <analisis.json> --review content/alerts/reviews/candiru-v2.json
```

No consume IA ni publica. Valida el contrato, exige cuatro imágenes de 1080 × 1350
y genera una carpeta única en `media/publicacion-revisada/`, con vista previa,
registro de revisión y ZIP. El ZIP contiene solo las cuatro diapositivas, el caption
y las instrucciones. Revisar visualmente antes de subir; el exportador no verifica
automáticamente la fidelidad de los textos respecto del informe original.
