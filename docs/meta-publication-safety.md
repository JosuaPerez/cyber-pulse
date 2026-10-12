# Publicación segura en Meta

## Autenticación

El token se envía en el encabezado HTTP `Authorization: Bearer ...`. No forma parte de query strings ni payloads, reduciendo la posibilidad de que aparezca en URLs, excepciones o logs.

## Integridad del carrusel

CyberPulse exige exactamente cinco rutas locales y cinco contenedores válidos de Meta. Si una subida o la creación de un item falla, no se ensambla ni publica un carrusel parcial.

## Resultado ambiguo

Antes de invocar `media_publish`, se guarda `meta_creation_id` y se activa `meta_publicacion_pendiente`. Si la petición termina en timeout, error HTTP no interpretable o JSON inválido, el bot:

1. No declara que la publicación falló.
2. No la reintenta automáticamente.
3. La marca para revisión manual.
4. Conserva el `creation_id` para investigar.

Esta política evita que una respuesta perdida provoque un post duplicado.

## Reconciliación

Lista los casos pendientes:

```powershell
cd cyberpulse-bot
python scripts/reconciliar_publicacion_meta.py listar
```

Después de verificar directamente en Instagram:

```powershell
# Si el post existe:
python scripts/reconciliar_publicacion_meta.py confirmar "CLAVE" "META_POST_ID"

# Solo si se confirmó que no existe:
python scripts/reconciliar_publicacion_meta.py reintentar "CLAVE" --confirmo-no-publicada
```

Nunca uses `reintentar` basándote únicamente en un timeout o en el log local. Primero comprueba la cuenta de Instagram.
