# Referencias visuales y decisiones · 18/10/2026

Estado: propuesta de diseño revisable; no cambia producción ni programa publicaciones.
Se revisaron las cuatro publicaciones públicas facilitadas por Josua en navegador.
No se descargaron ni reutilizaron sus fotografías, logos, capturas o ilustraciones.

## Qué tomamos y qué no

| Referencia | Idea aprovechable | Aplicación propia / límite |
| --- | --- | --- |
| [CodeCroc · aprendizaje de ciberseguridad](https://www.instagram.com/p/DecVpFrDemP/) | Jerarquía tipográfica fuerte, resaltado y visual protagonista. Se inspeccionaron portada y segunda slide. | La guía de paquetería v2 utiliza un teléfono y paquete vectoriales originales, fondo claro y cian CyberPulse. No copia su composición completa ni sus recursos. |
| [Rishi · carruseles](https://www.instagram.com/p/Dc8-CQGmJFu/) | Investigar referencias, reforzar las dos primeras entradas y variar formatos. | La slide 2 funciona por sí sola; cada paso aporta información nueva. No asumimos que todo carrusel se muestre exactamente dos veces. |
| [Swastik · algoritmo](https://www.instagram.com/p/DdnpQyHkhhw/) | Distinguir reels, carruseles e historias; pensar en atención y utilidad. | Sus diagramas son simplificaciones del autor, no documentación de Meta. No convertimos «sin likes = sin alcance» ni «tres segundos = éxito» en reglas. |
| [Boss Bae Steph · IA](https://www.instagram.com/p/Dd9-8hPkjJI/) | Trabajar por lotes, generar variantes y analizar aperturas. | Sus resultados comerciales y cifras son afirmaciones promocionales, no resultados esperables para CyberPulse ni prueba causal de la IA. No se envían comentarios ni se compra ningún recurso. |

## Propuesta visual concreta

- Se conserva el tema educativo de SMS: estas referencias no autorizan sustituirlo
  por un curso ni convertir una guía general en alerta de una campaña actual.
- `paquetes-editorial-v2.html`: guía de bolsillo 1080×1350 y carrusel educativo de
  cuatro slides. Una lámina de consulta y una secuencia narrativa son formatos distintos.
- Titulares grandes, ilustración original y jerarquía de lectura. El cian y el azul
  mantienen la marca; el fondo claro distingue guías de alertas urgentes.
- El texto breve no elimina condiciones: esperar un pedido no autentica un SMS;
  una señal aislada no demuestra fraude. Se mantiene INCIBE como fuente del consejo.
- La versión anterior permanece disponible; la v2 se exporta a un directorio separado.

## Siguiente iteración de alertas diarias · aún no implementada

Mantener el orden aprobado y las comprobaciones de evidencia del bot:

1. Portada: pregunta concreta para la persona afectada + producto y dato verificado.
2. Alcance: segunda entrada autónoma, no repetir el resumen; mostrar a quién aplica.
3. Mecanismo y límites: un diagrama pertinente, no un bloque genérico ni un hash largo.
4. Acción: dos o tres pasos específicos y una invitación útil a guardar.

Presupuesto editorial orientativo: un titular y una idea central por slide;
la evidencia puede exigir más texto. No truncar automáticamente versiones, negaciones,
condiciones o medidas. Nunca esconder información necesaria solo para respetar una
cuota de palabras. Llevar ampliación al caption sin perder la acción segura en la imagen.
Revisar esta dirección visual antes de modificar plantillas y publicar automáticamente.

## Algoritmo: evidencia frente a hipótesis

[Meta explica](https://about.fb.com/news/2023/06/how-ai-ranks-content-on-facebook-and-instagram/)
que combina diversas predicciones y señales; no hay una única interacción que
determine el valor de una publicación. Sus sistemas cubren distintas superficies.
Su explicación de 2023 es una base conceptual, no una fórmula completa de 2026.

[Meta anunció en 2024](https://about.fb.com/ltam/news/2024/05/ayudando-a-los-creadores-a-encontrar-nuevas-audiencias/)
cambios de distribución y prioridad al contenido original frente a copias idénticas.
Eso respalda crear recursos propios; no permite prometer alcance ni fechas de crecimiento.

Hipótesis de CyberPulse: menos lectura inicial y un ejemplo visual podrían mejorar
la comprensión. Contrastar a 24 y 72 horas con datos de la cuenta. No llamar a esta
comparación prueba A/B causal: tema, audiencia y momento también cambian.

## Uso de IA para crecer sin perder confianza

Flujo editorial propuesto, no nueva automatización:

1. Reunir fuentes y preguntas reales sin datos privados ni mensajes identificables.
2. Preparar una ficha de hechos, incertidumbres y acción verificable.
3. Pedir tres aperturas originales para principiantes; rechazar alarma no sustentada.
4. Elegir una, convertirla en reel, guía e historia con funciones distintas.
5. Revisar hechos, legibilidad y exportación antes de publicar.
6. Registrar métricas disponibles y observaciones; proponer el próximo cambio.

Prompt de trabajo reutilizable:

> Con esta ficha verificada y estas preguntas anónimas, propón tres aperturas para
> CyberPulse. Conserva condiciones, fechas y límites. No añadas cifras, incidentes,
> testimonios ni promesas de crecimiento. Para cada apertura, indica la conducta útil
> que aprenderá la audiencia y un visual original. Distingue hechos de hipótesis.

No necesita cambiar Gemini ni comprar otro proveedor. No hay auto-DMs, captación
por palabras clave ni cambios de permisos. Las nuevas piezas quedan para revisión.

## Exportar y revisar

```powershell
.venv\Scripts\python.exe scripts/render_parcel_editorial.py
```

Salida ignorada por Git: `cyberpulse-bot/media/content/2026-10-paquetes/editorial-v2/`.
Incluye `cheat-sheet-v2.png`, cuatro slides y `carousel-overview.png`.
El guion del reel y el calendario del paquete anterior siguen siendo borradores.
