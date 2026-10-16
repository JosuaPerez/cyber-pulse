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
