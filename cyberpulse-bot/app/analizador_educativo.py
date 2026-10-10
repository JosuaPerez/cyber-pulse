"""Generación de contenido educativo evergreen sin depender de fuentes RSS."""
import json
import logging
import os
import re
import time

from google.genai import types
from pydantic import ValidationError

from app.analizador import ErrorAnalisis, _resumir_errores
from app.esquemas import AnalisisIA, a_formato_legacy
from app.glosario import glosario_para_prompt

log = logging.getLogger("cyberpulse.analizador_educativo")

MODELO = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
MAX_INTENTOS = 3
ESPERA_BASE_API = 10
MARGEN_PROMPT = 0.85
TIPOS_EDUCATIVOS = {"concepto", "cheatsheet", "checklist", "comparativa", "tip"}
PATRON_CVE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
PATRON_ESTADISTICA = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*%|\b(?:más de|menos de|al menos|aproximadamente)\s+\d+",
    re.IGNORECASE,
)


def construir_system_prompt(tema: dict) -> str:
    """Construye instrucciones específicas para el tema evergreen recibido."""
    tipo = tema.get("tipo", "")
    if tipo == "cheatsheet":
        campos_items = """
- items: exactamente 3 a 4 objetos; cada uno debe tener sintaxis exacta y una explicacion de una sola línea (máximo 90 caracteres), sin párrafos.
- riesgos y mitigacion: listas vacías; no los desarrolles para este formato.
"""
    elif tipo == "checklist":
        campos_items = """
- items_checklist: exactamente 4 a 6 objetos; cada uno debe tener un campo paso con una acción breve de verificación (máximo 100 caracteres). Escribe pasos accionables en lenguaje natural, sin sintaxis de comandos, código ni prompts de terminal.
- items: null; riesgos y mitigacion: listas vacías; no los desarrolles para este formato.
"""
    elif tipo == "tip":
        campos_items = """
- tip_slides: exactamente 2 objetos. Cada uno debe tener texto breve (máximo 110 caracteres), 2 a 4 chips de texto corto (máximo 15 caracteres cada uno) y 2 a 3 stat-blocks con valor (máximo 10 caracteres) y etiqueta (máximo 20 caracteres).
- tip_bullets: exactamente 3 a 4 bullets accionables o memorables, de máximo 60 caracteres cada uno.
- Los stat-blocks deben ser cualitativos o expresar conocimiento general aceptado (por ejemplo, "ALTO" / "Riesgo"). No inventes porcentajes, conteos, fechas ni métricas. Si no existe un valor general confiable, usa un valor cualitativo, no una cifra inventada.
- items, items_checklist, riesgos y mitigacion: listas vacías; no los desarrolles para este formato.
"""
    else:
        campos_items = """
- riesgos: exactamente 3 consecuencias o errores relevantes, de máximo {riesgo_limite} car. cada uno.
- mitigacion: exactamente 3 acciones o pasos defensivos, de máximo {mitigacion_limite} car. cada uno.
""".format(
        riesgo_limite=int(90 * MARGEN_PROMPT),
        mitigacion_limite=int(100 * MARGEN_PROMPT),
    )
    return f"""Eres el creador de contenido educativo evergreen de CyberPulse (@CyberPulse89), una cuenta de ciberseguridad en español para estudiantes y profesionales de Blue Team.

TEMA:
{json.dumps(tema, ensure_ascii=False, indent=2)}

REGLAS:
1. El contenido es atemporal y educativo; no lo trates como una noticia ni inventes una fuente.
2. La slide 1 debe comenzar con un GANCHO fuerte que capte la atención durante los primeros 5-8 segundos de lectura.
3. Si el tipo es "cheatsheet", usa comandos seguros con sintaxis exacta. Si el tipo es "checklist", usa pasos de verificación en lenguaje natural, sin sintaxis de comandos. Si el tipo es "tip", usa contenido breve de alta recordación, sin comandos, checklist ni desarrollo narrativo largo.
4. Evita cualquier cifra, estadística o afirmación específica que no sea conocimiento general aceptado en el campo. No inventes CVEs, porcentajes, casos "según estudios" ni datos concretos; si el tema requiere uno, omítelo.
5. No incluyas CVEs en ningún campo. No incluyas exploits ni PoC funcionales.
6. El caption debe terminar con una pregunta breve y directa relacionada con el tema; no incluyas hashtags ni fuente.
7. Mantén el contenido claro, preciso y útil para defensa, sin presentar opiniones como hechos.

CAMPOS:
- es_relevante: siempre true para este tema educativo; motivo_descarte vacío.
- severidad: "medium".
- estado_explotacion: "desconocido".
- cves: lista vacía.
- portada_titulo (máx {int(50 * MARGEN_PROMPT)} car.): gancho breve y fuerte para la slide 1.
- portada_subtitulo (máx {int(110 * MARGEN_PROMPT)} car.): promesa educativa concreta.
- problema (máx {int(320 * MARGEN_PROMPT)} car.): contexto del concepto o problema.
- dato_tecnico (máx {int(220 * MARGEN_PROMPT)} car.): explicación técnica general, sin cifras inventadas.
{campos_items}
- caption (máx {int(1000 * MARGEN_PROMPT)} car.): texto para Instagram, sin hashtags ni fuente, terminado en pregunta.
- hashtags: de 3 a 5 strings, cada uno comenzando con # y sin espacios.
- hilo_x: exactamente 3 tweets educativos, sin numeración ni enlaces, de máximo {int(225 * MARGEN_PROMPT)} car. cada uno.

El tipo de contenido es: {tipo}.

{glosario_para_prompt()}"""


def verificar_contenido_educativo(analisis: AnalisisIA) -> list[str]:
    """Aplica reglas deterministas para evitar datos concretos no sustentados."""
    textos = " ".join(
        [analisis.portada_titulo, analisis.portada_subtitulo, analisis.problema,
         analisis.dato_tecnico, analisis.caption, *analisis.riesgos,
         *analisis.mitigacion, *analisis.hilo_x]
    )
    problemas = []
    if analisis.cves or PATRON_CVE.search(textos):
        problemas.append("el contenido educativo no puede incluir CVEs")
    if PATRON_ESTADISTICA.search(textos):
        problemas.append("el contenido educativo no puede incluir cifras o estadísticas no verificadas")
    if not analisis.caption.strip().endswith("?"):
        problemas.append("caption debe terminar en una pregunta")
    return problemas


def analizar_tema_educativo(client, tema: dict, modelo: str = MODELO) -> dict:
    """Analiza un tema evergreen y devuelve el formato legacy del carrusel."""
    if tema.get("tipo") not in TIPOS_EDUCATIVOS:
        raise ValueError(f"Tipo educativo inválido: {tema.get('tipo')!r}")
    tipo = tema["tipo"]

    config = types.GenerateContentConfig(
        system_instruction=construir_system_prompt(tema),
        response_mime_type="application/json",
        response_schema=AnalisisIA,
        temperature=0.2,
    )
    correccion = ""
    ultimo_error = "desconocido"

    for intento in range(1, MAX_INTENTOS + 1):
        try:
            contenido = "Genera el JSON completo para el tema educativo indicado en tus instrucciones."
            resp = client.models.generate_content(model=modelo, contents=contenido + correccion, config=config)
            if not resp.text:
                raise ValueError("respuesta vacía del modelo")

            analisis = AnalisisIA.model_validate_json(resp.text)
            if not analisis.es_relevante:
                raise ValueError("el contenido educativo debe marcar es_relevante=true")
            problemas = verificar_contenido_educativo(analisis)
            if problemas:
                raise ValueError("; ".join(problemas))

            datos = a_formato_legacy(
                analisis,
                "CyberPulse Educación",
                f"educativo://{tema['id']}",
            )
            datos["meta"]["familia"] = "educativo"
            datos["meta"]["tipo"] = tema["tipo"]
            if tipo == "cheatsheet":
                if not analisis.items or not 3 <= len(analisis.items) <= 4:
                    raise ValueError(
                        "el formato cheatsheet requiere entre 3 y 4 items"
                    )
                datos["items"] = [
                    {
                        "sintaxis": item.sintaxis.strip(),
                        "explicacion": item.explicacion.strip(),
                    }
                    for item in analisis.items
                ]
            elif tipo == "checklist":
                if not analisis.items_checklist or not 4 <= len(analisis.items_checklist) <= 6:
                    raise ValueError(
                        "el formato checklist requiere entre 4 y 6 pasos"
                    )
                datos["items_checklist"] = [
                    {"paso": item.paso.strip()}
                    for item in analisis.items_checklist
                ]
            elif tipo == "tip":
                if not analisis.tip_slides or len(analisis.tip_slides) != 2:
                    raise ValueError("el formato tip requiere exactamente 2 tip_slides")
                if not analisis.tip_bullets or not 3 <= len(analisis.tip_bullets) <= 4:
                    raise ValueError(
                        "el formato tip requiere entre 3 y 4 tip_bullets"
                    )
                datos["tip_slides"] = [
                    {
                        "texto": slide.texto.strip(),
                        "chips": [
                            {"texto": chip.texto.strip()} for chip in slide.chips
                        ],
                        "stats": [
                            {
                                "valor": stat.valor.strip(),
                                "etiqueta": stat.etiqueta.strip(),
                            }
                            for stat in slide.stats
                        ],
                    }
                    for slide in analisis.tip_slides
                ]
                datos["tip_bullets"] = [
                    bullet.strip() for bullet in analisis.tip_bullets
                ]
            return datos
        except ValueError as e:
            ultimo_error = _resumir_errores(e) if isinstance(e, ValidationError) else str(e)
            log.warning("Intento %d/%d rechazado: %s", intento, MAX_INTENTOS, ultimo_error)
            correccion = (
                "\n\nTu respuesta anterior fue RECHAZADA por estos motivos. "
                f"Genera el JSON completo de nuevo corrigiéndolos:\n{ultimo_error}"
            )
        except Exception as e:
            ultimo_error = f"error de API: {e}"
            log.warning("Intento %d/%d falló: %s", intento, MAX_INTENTOS, e)
            if intento < MAX_INTENTOS:
                time.sleep(ESPERA_BASE_API * 2 ** (intento - 1))

    raise ErrorAnalisis(
        f"Sin análisis educativo válido tras {MAX_INTENTOS} intentos. Último problema: {ultimo_error}"
    )
