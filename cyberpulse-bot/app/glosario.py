"""Glosario y reglas de estilo para adaptar contenido de ciberseguridad al español.

Este archivo es solo DATOS: edítalo cuando quieras ajustar el estilo de CyberPulse
sin tocar la lógica del bot. Cada cambio se refleja automáticamente en el prompt.
"""

# Términos que se dejan en inglés tal cual: la comunidad hispanohablante ya los usa así.
MANTENER_EN_INGLES = [
    "zero-day", "ransomware", "malware", "exploit", "payload", "phishing", "backdoor",
    "botnet", "infostealer", "spyware", "rootkit", "loader", "dropper", "webshell",
    "sandbox", "hardening", "red team", "blue team", "threat intelligence", "bug bounty",
    "RCE", "XSS", "SQL injection", "DDoS", "C2", "IOC", "TTP", "PoC",
    "CVE", "CVSS", "EPSS", "KEV", "MITRE ATT&CK",
    "EDR", "XDR", "SIEM", "WAF", "VPN", "MFA",
]

# Términos que SÍ se traducen (inglés -> español).
TRADUCIR = {
    "patch": "parche",
    "vulnerability": "vulnerabilidad",
    "threat actor": "actor de amenazas",
    "advisory": "aviso de seguridad",
    "supply chain attack": "ataque a la cadena de suministro",
    "privilege escalation": "escalada de privilegios",
    "lateral movement": "movimiento lateral",
    "data breach": "filtración de datos",
    "brute force": "fuerza bruta",
    "authentication bypass": "omisión de autenticación",
    "remote code execution": "ejecución remota de código",
    "proof of concept": "prueba de concepto (PoC)",
    "actively exploited": "explotada activamente",
    "in the wild": "en entornos reales",
    "mitigation": "mitigación",
    "attack surface": "superficie de ataque",
}

# Cómo conservar el nivel de certeza de la fuente (crítico para la credibilidad).
CERTEZA = {
    "may / might / could": "podría / podrían",
    "is being exploited / exploited in the wild": "se está explotando activamente",
    "allegedly / reportedly": "presuntamente / según se informa",
    "researchers believe / say": "según investigadores de <empresa>",
    "no evidence of exploitation": "sin evidencia de explotación hasta el momento",
}

REGLAS_ESTILO = [
    "Español neutro (válido para España y Latinoamérica): sin regionalismos ni voseo. Trato de tú.",
    "Tono directo, técnico y de autoridad. Sin clickbait, sin exclamaciones y sin mayúsculas sostenidas.",
    "No traduzcas nombres propios: productos, empresas, grupos de amenaza (ej. Lazarus, APT29), "
    "familias de malware, CVEs, comandos, rutas, hashes ni nombres de archivo.",
    "Si usas un término técnico poco común, explícalo la primera vez en máximo 6 palabras entre paréntesis.",
    "Los IOCs (dominios, URLs, IPs) se escriben 'defanged': hxxps://ejemplo[.]com, 192[.]0[.]2[.]1.",
    "Las mitigaciones empiezan con un verbo en imperativo (Actualiza, Restringe, Habilita, Monitorea).",
]


def glosario_para_prompt() -> str:
    """Devuelve el glosario formateado para insertarlo en el prompt del sistema."""
    mantener = ", ".join(MANTENER_EN_INGLES)
    traducir = "\n".join(f"- {en} -> {es}" for en, es in TRADUCIR.items())
    certeza = "\n".join(f"- {en} -> {es}" for en, es in CERTEZA.items())
    estilo = "\n".join(f"- {r}" for r in REGLAS_ESTILO)
    return (
        f"TÉRMINOS QUE SE DEJAN EN INGLÉS:\n{mantener}\n\n"
        f"TÉRMINOS QUE SE TRADUCEN:\n{traducir}\n\n"
        f"NIVEL DE CERTEZA (no lo aumentes nunca):\n{certeza}\n\n"
        f"REGLAS DE ESTILO:\n{estilo}"
    )
