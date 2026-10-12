# Política de seguridad

## Reportar una vulnerabilidad

No publiques credenciales, tokens, capturas del archivo `.env` ni detalles explotables en un issue público. Reporta la vulnerabilidad de forma privada mediante GitHub Private Vulnerability Reporting cuando esté disponible para el repositorio.

Incluye una descripción del impacto, los pasos mínimos para reproducir el problema y la versión o commit afectado. No incluyas datos personales ni credenciales reales.

## Secretos

- El archivo `cyberpulse-bot/.env` es exclusivamente local y nunca se versiona.
- `.env.example` contiene nombres de variables y valores de ejemplo, nunca secretos reales.
- Los despliegues deben obtener sus secretos del entorno o de un gestor de secretos.
- Los workflows de CI solo usan credenciales ficticias y `DRY_RUN=true`.
- Ante cualquier exposición, primero se revoca el secreto y después se investiga el origen.

## Publicación segura

Las pruebas y los entornos de desarrollo deben ejecutar el bot con:

```env
DRY_RUN=true
PUBLICAR_EN_X=false
```

La publicación real solo debe habilitarse después de revisar las imágenes y el texto generado.

## Alcance

El proyecto está en desarrollo activo. Las vulnerabilidades en autenticación, manejo de secretos, publicación duplicada, SSRF y validación de contenido se consideran de alta prioridad.

