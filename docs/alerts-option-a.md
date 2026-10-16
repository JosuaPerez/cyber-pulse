# Alertas diarias · dirección aprobada: opción A

La opción A se llama `clara` en configuración. Identidad cian/azul, jerarquía
legible y cuatro diapositivas: resumen, contexto/alcance reportado, detalle con
riesgos y fuente, y medidas al cierre. No se fuerza
a que todas las noticias sean actualizaciones ni se inventan versiones. El
acento cian es de marca; la severidad es un dato independiente.

## Activación gradual

1. Ejecutar las pruebas, lint y build; exportar muestra normal y textos largos.
2. Revisar noticias representativas, sin ejecutar publicación real.
3. Abrir PR del código y documentación; revisar CI antes de fusionar.
4. En el entorno de pruebas, usar `ALERTAS_VARIANTE=clara` y `DRY_RUN=true`.
5. Revisar el carrusel pendiente antes de decidir activar en el despliegue real.

Este cambio no modifica el `.env` privado ni `DRY_RUN`, ni publica contenido.
`ALERTAS_VARIANTE=clasica` sigue siendo el valor predeterminado y el rollback.
`generar_imagenes_carrusel(datos, variante_alerta="clasica")` permite seleccionar
el respaldo explícitamente. Una configuración inválida falla antes de publicar;
no se cambia silenciosamente de diseño. Educativos y cheat sheets no cambian.

Con Vite activo y desde `cyberpulse-bot`:

```powershell
python -X utf8 -m app.demo_alerta_editorial --variant clara --output media/alert-option-a
python -X utf8 -m app.demo_alerta_editorial --variant clara --stress --output media/alert-option-a-stress
```

Ambos comandos usan un ejemplo ficticio, no llaman a IA ni a las APIs de redes.
La producción toma las fuentes y el estado de explotación del análisis existente.
Si falta un dato se indica; el render rechaza un desbordamiento, no lo publica
recortado. La ausencia de CVE no significa ausencia de vulnerabilidad.

## Lectura rápida: cuatro diapositivas

- 1: título reconocible y consecuencia principal; sin tarjetas que solo anuncien
  secciones. El prompt de `clara` prioriza utilidad, producto y lenguaje claro.
- 2: el campo de problema existente, que incluye contexto y exposición reportada.
  No es una clasificación individual ni inventa versiones cuando la fuente calla.
- 3: detalle técnico y los tres riesgos, sin resumirlos automáticamente ni perder
  puntos; los CVEs aparecen aquí si fueron aportados.
- 4: las tres mitigaciones ya validadas y un recordatorio para guardar el post
  hasta confirmar la actualización. La portada remite a esta diapositiva.

No se cambia el esquema de la IA. El formato clásico y los educativos conservan
cinco imágenes. Instagram exige el número planificado (4 o 5), no simplemente un
número dentro de un rango: un carrusel incompleto no inicia subidas. X conserva
la relación entre texto e imágenes mediante índices distintos para 4 y 5.

La fecha "PREPARADO ... UTC" es de generación, no la fecha del incidente. La fecha
de fuente solo aparece si se aporta como metadato `fecha_fuente`.

Para comparar con el caso real congelado de Mozilla del 13/10/2026, sin volver a
analizarlo con IA ni presentarlo como noticia nueva:

```powershell
python -X utf8 -m app.demo_alerta_editorial --variant clara --example firefox --output media/alert-compact-firefox-v2
```

Ese ejemplo aporta explícitamente `visual_apoyo.tipo=firefox_version` y
`visual_apoyo.version=158`, revisados contra el aviso de Mozilla. La portada y el
alcance muestran la versión corregida; el cierre incluye un mockup ilustrativo
de «Acerca de Firefox», no una captura del equipo del lector. El render valida
el formato de versión y la URL HTTPS del aviso en mozilla.org, pero no consulta
el aviso ni verifica automáticamente que su texto contenga esa versión: esa
comprobación corresponde a la preparación editorial. Sin metadatos válidos no
se muestra el visual, ni se deduce una versión del titular.

Los renders anteriores no se borran. Usa solo las rutas devueltas por el generador,
no todos los PNG de una carpeta: podría quedar un slide antiguo de otro formato.
El manifiesto de `DRY_RUN` enumera las rutas exactas en orden.

## Ajuste tras la primera noticia real

El prompt de `clara` prioriza un gancho reconocible y distingue al administrador
del anfitrión del usuario de un proveedor. Las mitigaciones deben ser aplicables
al rol, sin presentar controles complementarios como sustitutos del parche.
La recomendación sin explicar «jailers» se rechaza y reintenta en esta variante.
Esto mejora la redacción, pero no demuestra automáticamente que cada acción sea
correcta para todos los productos: sigue siendo necesaria la revisión editorial.

Para escapes explícitos se aplica una ficha editorial fija: gancho por rol,
alcance condicionado y tres acciones generales para consultar el aviso, seguir
las medidas del proveedor y verificar su aplicación. También se normalizan
caption e hilo para no ampliar el alcance ni exigir un reinicio universal.
No son instrucciones específicas de instalación ni una afirmación de que exista
un parche para todos los productos. El dato técnico y los riesgos siguen pasando
por las comprobaciones contra la fuente. La severidad editorial se limita a high
si el modelo eligió critical sin explotación activa reportada en este caso.

El código busca primero una frase apta en el cuerpo del artículo/resumen, sin
contar el título, y conserva esa cita: no depende de que la IA la copie bien.
Si no encuentra una, no aplica la ficha; la selección opcional de la IA todavía
debe superar las comprobaciones de evidencia. `visual_tipo=vm_isolation` requiere `visual_evidencia`
literal, de 20–300 caracteres, presente en el texto extraído y con referencias a
VM/invitado, anfitrión y escape (incluye «breaking out»). La evidencia queda en
metadatos para revisión, no en el dibujo. No se selecciona por el nombre del CVE.
Son comprobaciones de texto, no comprensión semántica: aunque se excluyen algunas
negaciones explícitas, no verifican por sí solas todos los matices, alcance ni vigencia.
El render usa etiquetas fijas, nunca HTML o
etiquetas arbitrarias de la IA. Sin selección válida conserva el formato textual.
Firefox mantiene su visual y su contrato explícito de versiones, sin reutilizarlo
para Linux. No hay generación automática de diagramas para cualquier noticia.

El esquema acepta análisis antiguos sin los dos campos nuevos. El formato clásico
y los educativos conservan su salida. Si no se logra extraer un artículo o resumen
de al menos 160 caracteres, el analizador falla antes de llamar a la IA; el título
no cuenta para ese mínimo. Ese umbral evita el análisis de un título aislado,
pero no acredita la calidad ni exhaustividad de un resumen.

Ejemplo editorial congelado, contrastado con [PWNAI Research](https://www.pwn.ai/blog/pwnescape):

```powershell
python -X utf8 -m app.demo_alerta_editorial --variant clara --example pwnescape --output media/pwnescape-ajustada
python -X utf8 -m app.demo_alerta_editorial --variant clara --example pwnescape --stress --output media/pwnescape-limites
```

La muestra usa severidad `high` según la política editorial del bot, no como
transcripción de la calificación del investigador. No afirma explotación activa.

Para repetir una revisión con IA sobre una URL real de los dominios permitidos:

```powershell
python -X utf8 -m app.revisar_alerta --url https://thehackernews.com/2026/10/critical-pwnescape-linux-kernel.html --title "Critical PwnEscape Linux Kernel Vulnerability Lets Guest VMs Read Host Memory"
```

Consume cuota de Gemini. Requiere Vite y las dependencias fijadas, incluido
trafilatura. Fuerza `clara`, no importa publicadores, no consulta/reserva RSS ni
modifica el historial; guarda cada revisión en una carpeta única bajo
`media/revision-alertas/`, excluida de Git. El `.env` no se modifica. Los errores
de API o de contenido no activan publicación ni un modo alternativo.
