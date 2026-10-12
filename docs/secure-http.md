# Descargas HTTP seguras

CyberPulse trata las URLs de feeds y artículos como entradas no confiables. Todas
las descargas editoriales pasan por `app/http_seguro.py` antes de abrir una
conexión.

## Controles aplicados

- Solo se admite HTTPS y el puerto 443.
- El host debe pertenecer a la lista explícita de medios configurados.
- Se rechazan credenciales embebidas en la URL.
- La resolución DNS se comprueba y debe devolver únicamente direcciones IP
  públicas.
- Las redirecciones automáticas están desactivadas. Cada destino se vuelve a
  validar y se permiten como máximo tres saltos.
- La respuesta se procesa en streaming. Se controla tanto `Content-Length` como
  el número real de bytes recibidos.
- Los feeds tienen un límite predeterminado de 2 MB y los artículos de 5 MB.

Los límites pueden ajustarse mediante `RSS_MAX_BYTES`, `ARTICULO_MAX_BYTES` y
`HTTP_MAX_REDIRECCIONES`. Los dominios se modifican deliberadamente en código:
agregar una fuente es un cambio revisable, no una configuración operativa libre.

## Comportamiento ante rechazos

Si un feed no supera los controles, el lector registra una advertencia y prueba
la siguiente fuente. Si el artículo enlazado no puede descargarse, el analizador
usa el resumen incluido en el RSS. Nunca se intenta acceder a un destino fuera
de la lista permitida.

## Riesgo residual

La validación DNS se realiza antes de que la biblioteca HTTP abra la conexión.
Un atacante con control del DNS de un dominio permitido podría intentar cambiar
la resolución entre ambos momentos. La lista reducida de dominios editoriales y
HTTPS disminuyen este riesgo. Un endurecimiento futuro puede fijar la IP validada
en la conexión o ejecutar estas descargas en una red aislada sin acceso a redes
privadas ni al endpoint de metadatos de la nube.
