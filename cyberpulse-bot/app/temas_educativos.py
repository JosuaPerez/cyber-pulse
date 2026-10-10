"""Temas evergreen de ejemplo para generar contenido educativo bajo demanda.

Los briefs incluidos son placeholders: deben revisarse y completarse antes de
usar estos temas en serio.
"""

TEMAS_EDUCATIVOS = [
    {
        "id": "nmap-reconocimiento-basico",
        "tipo": "cheatsheet",
        "brief": (
            "Los 4 comandos de nmap que todo analista usa en un reconocimiento autorizado: "
            "escaneo de puertos básico (nmap -sV), detección de SO (-O), script de "
            "vulnerabilidades conocidas (--script vuln) y escaneo sigiloso (-sS). Para cada "
            "uno: qué hace exactamente y qué información obtienes. Enfatizar que esto es para "
            "auditorías autorizadas sobre infraestructura propia o con permiso explícito."
        ),
    },
    {
        "id": "filtros-wireshark-esenciales",
        "tipo": "cheatsheet",
        "brief": (
            "5 filtros de Wireshark que un analista SOC usa a diario para detectar tráfico "
            "sospechoso: tráfico HTTP sin cifrar (http), intentos de login fallidos repetidos, "
            "DNS queries anómalas (dns), tráfico hacia puertos no estándar, y paquetes con "
            "flags TCP inusuales (tcp.flags). Cada filtro con la sintaxis exacta de Wireshark "
            "y qué patrón de ataque suele indicar."
        ),
    },
    {
        "id": "codigos-http-que-indican-ataque",
        "tipo": "checklist",
        "brief": (
            "Qué códigos de estado HTTP en tus logs de servidor deberían hacerte sospechar: "
            "ráfagas de 401/403 (fuerza bruta o enumeración), 500 repetidos en el mismo "
            "endpoint (posible intento de inyección rompiendo el backend), 404 en rutas "
            "inusuales como /admin o /.env (escaneo automatizado), y 200 inesperados en rutas "
            "que deberían requerir autenticación. Formato de checklist de lo que revisar en "
            "un log, no solo teoría."
        ),
    },
    {
        "id": "zero-day-explicado",
        "tipo": "concepto",
        "brief": (
            "Explicar qué es un Zero-Day en términos simples para alguien que nunca ha "
            "escuchado el término: la diferencia entre una vulnerabilidad conocida con parche "
            "disponible y una que el fabricante aún no sabe que existe, por qué el nombre "
            "'zero day' viene de los cero días que tuvo el vendor para reaccionar, y por qué "
            "son tan valiosos en el mercado negro. Sin inventar cifras de precios de mercado "
            "negro si no hay una fuente clara; mantenerlo conceptual."
        ),
    },
    {
        "id": "cvss-en-60-segundos",
        "tipo": "concepto",
        "brief": (
            "Cómo leer un puntaje CVSS (0 a 10) sin ser experto: qué significan los rangos "
            "(bajo, medio, alto, crítico), y los 3 factores que más mueven el puntaje para un "
            "lector no técnico: si se puede explotar remotamente sin autenticación, si "
            "requiere interacción del usuario, y el impacto real (confidencialidad, "
            "integridad, disponibilidad). El objetivo es que después de leer esto, alguien "
            "entienda por qué un 9.8 es grave y un 4.2 no lo es tanto."
        ),
    },
]
