---
name: cyberpulse-editorial
description: Investiga, redacta o revisa noticias, carruseles, captions y guiones de ciberseguridad para CyberPulse con fuentes verificables y lenguaje accesible. Úsala para contenido editorial de CyberPulse, no para cambios de código sin contenido.
---

# CyberPulse editorial

## Clasificar antes de redactar

Distingue vulnerabilidad, incidente, investigación y riesgo de política/comportamiento. No fuerces IOCs, versiones, severidad de CVE o «tu dispositivo» en temas de gobernanza. Si exportas al bot, consulta sus valores actuales: una investigación puede requerir tratamiento manual si el contrato no la representa.

## Establecer qué sabemos

- Abre las fuentes primarias actuales: proveedor, investigador original y, si corresponde, autoridad oficial. Una noticia secundaria sirve para descubrirlas, no para reemplazar la verificación. Registra URL, fecha del hecho, fecha de publicación/actualización y momento de consulta.
- Verifica la asociación entre producto, nombre del fallo, CVE, boletín, versiones y medidas. No combines identificadores de hallazgos distintos. Si una corrección cambia la identidad, revisa títulos, cuerpo, pies, captions y metadatos, no solo una slide.
- Distingue posibilidad técnica, demostración pública, reportes atribuidos de explotación y ataques confirmados. El silencio de una fuente significa desconocido, no «sin ataques». No generalices observaciones de un proveedor a todas las instalaciones.
- Conserva condiciones y límites. Una actualización futura no está distribuida todavía; una clave de certificadora no es una contraseña personal. Atribuye declaraciones de una empresa que no hayas corroborado independientemente.
- Presenta contradicciones sin resolverlas por intuición. Si afectan identidad, alcance o remediación, entrega borrador pendiente de verificación en lugar de afirmar que está listo para publicar.
- Vincula cada medida concreta a su fuente. Separa orientación editorial general de remediación específica. No inventes versiones, comandos, hashes, cifras ni garantías de protección.

## Convertir evidencia en contenido

Para alertas en carrusel, usa como punto de partida: gancho → a quién concierne → mecanismo y límites → acción concreta. Adapta la estructura al tema; no impongas cuatro slides a un reel o cheat sheet.

- Abre con una consecuencia o pregunta comprensible; explica siglas como RCE y evita alarmismo. Un gancho no puede prometer más que la evidencia.
- Una idea principal por bloque; elimina repeticiones entre slides y entre resumen e ilustración. El caption amplía, no transcribe todo el carrusel.
- Propón medidas distintas para las audiencias pertinentes, sin rellenar con tres variantes de «consulta la fuente». Si faltan medidas suficientes, no inventes para satisfacer una plantilla.
- Cierra con una acción útil y un CTA coherente. Guardar tiene sentido si hay algo que consultar o completar; no prometas crecimiento ni alcance por usarlo.
- La severidad debe explicitar su origen: escala del proveedor, CVSS o prioridad editorial. No conviertas escalas distintas automáticamente.
- Marca diagramas y mockups como ilustrativos cuando puedan confundirse con pruebas reales. Conserva referencias legibles y diferencia fecha de preparación de fecha del incidente.

## Exportar y revisar

Antes de generar datos, lee `cyberpulse-bot/app/alertas_v3.py` y `cyberpulse-bot/app/limites.py` desde la raíz del repositorio. Usa el esquema y límites actuales, no los de conversaciones anteriores. No cambies el contrato para acomodar una pieza sin que la tarea incluya código.

Las citas del contrato automático deben ser evidencia admitida por el validador, no etiquetas bibliográficas disfrazadas de citas. Validar el esquema o encontrar una coincidencia literal no demuestra veracidad semántica. No atribuyas validación automática a una investigación manual ni agregues sellos para saltar controles. Si existe `scripts/build_news_review.py`, inspecciónalo antes de reutilizarlo: puede contener noticias y fechas fijas.

Revisa el render final en tamaño móvil: texto completo, orden correcto, referencias cruzadas, ausencia de duplicación y cortes, contraste y CTA. Entrega el estado real: borrador, verificado editorialmente o pendiente de aprobación, con fuentes e incertidumbres. Una vista previa no es una publicación. Publicar, programar o activar el bot requiere autorización dentro del alcance actual; no se deduce de aprobar el estilo.
