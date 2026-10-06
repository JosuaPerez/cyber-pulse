"""Temas evergreen de ejemplo para generar contenido educativo bajo demanda.

Los briefs incluidos son placeholders: deben revisarse y completarse antes de
usar estos temas en serio.
"""

TEMAS_EDUCATIVOS = [
    {
        "id": "que-es-zero-day",
        "tipo": "concepto",
        "brief": "Explica qué es una vulnerabilidad zero-day, cómo se diferencia de una vulnerabilidad conocida y qué señales debe vigilar un equipo Blue Team.",
        "usado": False,
    },
    {
        "id": "cheatsheet-linux-investigacion",
        "tipo": "cheatsheet",
        "brief": "Reúne comandos Linux seguros y habituales para revisar procesos, red, usuarios y persistencia durante una investigación defensiva.",
        "usado": False,
    },
    {
        "id": "checklist-phishing",
        "tipo": "checklist",
        "brief": "Propón una checklist práctica para triagear un correo sospechoso sin abrir enlaces ni ejecutar adjuntos.",
        "usado": False,
    },
    {
        "id": "comparativa-ids-ips",
        "tipo": "comparativa",
        "brief": "Compara IDS e IPS desde la perspectiva de detección, prevención, despliegue y respuesta operativa de un equipo defensivo.",
        "usado": False,
    },
    {
        "id": "que-es-principio-menor-privilegio",
        "tipo": "concepto",
        "brief": "Explica el principio de menor privilegio con ejemplos defensivos aplicables a identidades, servicios y accesos administrativos.",
        "usado": False,
    },
]


def siguiente_tema_pendiente():
    """Devuelve el primer tema todavía no usado, o None si no quedan temas."""
    return next((tema for tema in TEMAS_EDUCATIVOS if not tema["usado"]), None)


def marcar_usado(identificador: str) -> None:
    """Marca como usado el tema indicado; falla si el identificador no existe."""
    for tema in TEMAS_EDUCATIVOS:
        if tema["id"] == identificador:
            tema["usado"] = True
            return
    raise ValueError(f"Tema educativo inexistente: {identificador}")
