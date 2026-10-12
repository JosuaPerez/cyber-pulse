# Estados, reservas y reintentos

## Propósito

La persistencia evita que dos workers procesen simultáneamente la misma noticia y que una noticia defectuosa bloquee indefinidamente el resto del feed.

## Estados persistidos

- `detectada`: candidata registrada y todavía no analizada.
- `analizada`: Gemini produjo contenido válido.
- `renderizada`: las slides fueron generadas.
- `publicada_meta`: Meta confirmó la publicación.
- `descartada`: la noticia no es publicable.
- `fallida`: ocurrió un error recuperable o se agotaron los intentos.

Los campos auxiliares distinguen el estado operativo:

- `reserva_hasta`: concesión temporal que impide procesamiento concurrente.
- `proximo_reintento_en`: instante UTC antes del cual no se puede reintentar.
- `requiere_revision`: marca terminal para contenido agotado o pendiente de aprobación humana.
- `intentos`: número de fallos acumulados.

## Selección

Una noticia solo es elegible cuando:

1. No está publicada ni descartada.
2. No requiere revisión manual.
3. No alcanzó `MAX_INTENTOS_PUBLICACION`.
4. Llegó su fecha de reintento.
5. No tiene una reserva vigente.

La reserva se realiza con un único `UPDATE` condicional. Solo el worker cuyo `rowcount` sea uno puede continuar.

## Backoff

La demora se calcula como:

```text
REINTENTO_BASE_SEGUNDOS * 2 ** (intentos - 1)
```

Con los valores predeterminados, los reintentos ocurren después de 5 y 10 minutos. El tercer fallo marca el registro para revisión manual.

## Recuperación

Una reserva expirada permite volver a reclamar una noticia interrumpida. En `DRY_RUN`, el contenido renderizado queda marcado para revisión manual y no se genera repetidamente.

Después de aprobar o corregir manualmente un registro, se puede devolver a la cola mediante `reanudar_publicacion(clave_historial)`. Esta operación limpia intentos y reservas, pero no elimina el registro ni su identidad de deduplicación.

La confirmación ambigua de Meta se tratará en una fase separada: un timeout de publicación no debe interpretarse automáticamente como fallo ni provocar una republicación.
