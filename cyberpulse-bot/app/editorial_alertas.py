"""Contrato editorial común de las alertas claras; independiente de cada noticia."""

import re
from typing import Literal

from pydantic import BaseModel, Field

INDICADOR = re.compile(r"\b[0-9a-f]{32,64}\b|\b[a-z0-9-]+(?:\[\.\][a-z0-9-]+)+\b|\b(?:\d{1,3}\.){3}\d{1,3}\b|\b(?:[a-z0-9-]+\.)+(?:com|net|org|io|xyz|ru|cn|info)\b", re.IGNORECASE)
LENGUAJE_CLARO = {"screening server": "filtro de objetivos", "servidor de screening": "filtro de objetivos",
                  "C2 server": "servidor de control", "command-and-control server": "servidor de control",
                  "logs": "registros de actividad", "log": "registro de actividad",
                  "screening": "selección de objetivos", "payload": "código entregado",
                  "C2": "servidor de control", "IOC": "indicadores técnicos",
                  "SHA-256": "huella técnica", "SHA256": "huella técnica", "Ad server": "servidor de anuncios"}


def texto_claro(texto: str) -> str:
    for termino, traduccion in LENGUAJE_CLARO.items():
        texto = re.sub(r"\b" + re.escape(termino) + r"\b", traduccion, texto, flags=re.IGNORECASE)
    return texto


class AccionEditorial(BaseModel):
    rol: Literal["personas", "administradores"]
    texto: str = Field(min_length=5, max_length=90)
    orientacion_general: bool
    evidencia: str = Field(max_length=300)


class NodoEditorial(BaseModel):
    texto: str = Field(min_length=2, max_length=26)
    evidencia: str = Field(min_length=10, max_length=300)


class EditorialAlerta(BaseModel):
    # Valor por compatibilidad con fichas guardadas; el analizador nuevo lo exige explícito.
    tipo_noticia: Literal["incidente", "vulnerabilidad", "riesgo_operativo"] = "incidente"
    gancho: str = Field(min_length=8, max_length=50)
    resumen: str = Field(min_length=15, max_length=110)
    audiencia: Literal["general", "administradores", "mixta"]
    hecho: str = Field(min_length=15, max_length=110)
    alcance: str = Field(min_length=25, max_length=240)
    limite: str = Field(min_length=15, max_length=100)
    temporalidad: Literal["historica", "vigencia_no_confirmada"]
    evidencia_temporal: str = Field(max_length=300)
    detalle: str = Field(min_length=15, max_length=180)
    acciones: list[AccionEditorial] = Field(min_length=1, max_length=3)
    caption: str = Field(min_length=30, max_length=500)
    evidencias: list[str] = Field(min_length=1, max_length=4)
    visual: Literal["resumen", "cadena", "comparacion"]
    nodos: list[NodoEditorial] = Field(max_length=3)
    evidencia_relacion: str = Field(max_length=300)


def cita_presente(cita: str, fuente: str) -> bool:
    def normalizar(valor):
        return " ".join(valor.split()).casefold()
    return 10 <= len(cita.strip()) <= 300 and normalizar(cita) in normalizar(fuente)


# Filtro conservador, no una prueba de implicación semántica. Controles desconocidos
# quedan para revisión; mencionar un ataque no respalda una recomendación.
CONTROLES = (
    r"bloqueador\w*.*(?:anuncio|publicidad)|ad[- ]?block\w*",
    r"actualiz\w*|parche\w*|updat\w*|patch\w*|\bhotfix(?:es)?\b|\bfix(?:es)?\b",
    r"copia\w* de seguridad|respald\w*|backups?",
    r"autenticación multifactor|doble factor|multifactor|two[- ]factor|\bMFA\b",
    r"ayuda especializada|expert help|specialist support",
    r"política\w* de uso|acceptable[- ]use polic\w*|usage polic\w*",
    r"capacit\w*|formación|train\w*|educat\w*",
    r"herramientas? aprobad\w*|approved (?:AI )?tools?",
    r"retención de datos|data retention",
    r"rot\w*.*(?:claves|credenciales)|rotat\w*.*(?:keys|credentials)",
    r"desinstal\w*|uninstall\w*",
)
RECOMENDACION = re.compile(
    r"\b(recommend\w*|should|must|advis\w*|urge\w*|use|install|enable|apply|keep|"
    r"rotate|recomienda\w*|debe\w*|aconseja\w*|usa|instala|activa|aplica|rota)\b", re.IGNORECASE)
NEGACION = re.compile(r"\b(not|never|without|cannot|no|nunca|sin)\b|n['’]t\b", re.IGNORECASE)
CONSULTAS = {
    "administradores": "Consulta el aviso y verifica con tu equipo qué medidas corresponden a tu entorno.",
    "personas": "Consulta la fuente o pide ayuda al proveedor antes de asumir que estás afectado.",
}
CONSULTAS_ADICIONALES = {
    "Revisa las medidas del aviso oficial y verifica su aplicación.",
    "Consulta la fuente o al proveedor para comprobar si esta noticia te afecta.",
    "Verifica qué información falta antes de asumir que tu equipo está afectado.",
    "Consulta el informe con tu equipo de seguridad para comprobar qué medidas son aplicables.",
}


def respaldo_accion(texto: str, evidencia: str) -> bool:
    """Solo admite familias conocidas con recomendación explícita, sin negación."""
    # Una condición de imposibilidad de actualizar no niega la instrucción
    # de desinstalar. Se reconoce solo esta construcción, no se borra cualquier
    # negación de una recomendación.
    instruccion = re.split(r"\b(?:si|cuando|if|when)\b", texto, maxsplit=1, flags=re.IGNORECASE)[0]
    if NEGACION.search(instruccion) or not RECOMENDACION.search(evidencia):
        return False
    controles = [p for p in CONTROLES if re.search(p, instruccion, re.IGNORECASE)]
    if re.search(r"desinstal\w*|uninstall\w*", instruccion, re.IGNORECASE):
        evidencia = re.sub(
            r"\bwho cannot (?:upgrade|update)(?: to a secure version)?(?= are advised to uninstall)",
            "", evidencia, flags=re.IGNORECASE)
    # Una negación sobre Composer no invalida otra oración que recomienda un parche.
    # Se mantienen juntas las cláusulas de una oración para no perder su negación.
    frases = re.split(r"(?<=[.!?;])\s+|\n+", evidencia)
    return bool(controles) and all(
        any(not NEGACION.search(frase) and RECOMENDACION.search(frase)
            and re.search(p, frase, re.IGNORECASE) for frase in frases)
        for p in controles)


def caption_temporal(e: EditorialAlerta) -> str:
    if e.tipo_noticia == "riesgo_operativo":
        return f"Riesgo de uso y política, no confirmación de una brecha. {e.hecho} {e.limite} ¿Qué práctica revisarás con tu equipo?"
    periodo = ("Hechos históricos documentados; actividad actual no confirmada."
               if e.temporalidad == "historica" else
               "Según el informe; la vigencia actual no está confirmada.")
    return f"{periodo} {e.hecho} {e.limite} ¿Qué necesitas comprobar en tu caso?"


def fragmentos_fuente(fuente: str) -> dict[str, str]:
    partes = []
    for frase in re.split(r"(?<=[.!?])\s+|\n+", fuente):
        for inicio in range(0, len(frase), 240):
            fragmento = frase[inicio:inicio + 240].strip()
            if len(fragmento) >= 10:
                partes.append(fragmento)
    return {f"FUENTE_{i:03}": texto for i, texto in enumerate(partes, 1)}


def resolver_editorial(e: EditorialAlerta, fragmentos: dict[str, str]) -> tuple[EditorialAlerta, list[str]]:
    """Resuelve IDs a texto original; no acepta IDs desconocidos como evidencia."""
    data = e.model_dump()
    data["evidencias"] = [fragmentos.get(cita, cita) for cita in e.evidencias]
    for key in ["evidencia_temporal", "evidencia_relacion"]:
        data[key] = fragmentos.get(data[key], data[key])
    ajustes = []
    for campo in ["gancho", "resumen", "hecho", "alcance", "limite", "detalle", "caption"]:
        original = data[campo]
        if campo == "detalle" and INDICADOR.search(original):
            # No se recorta el indicador: se conserva en el análisis técnico original.
            data[campo] = data["resumen"]
            ajustes.append("El detalle con indicadores se remitió al informe; se usó el resumen factual en el carrusel.")
        data[campo] = texto_claro(INDICADOR.sub("referencia del informe", data[campo]))
        if data[campo] != original:
            ajustes.append(f"Lenguaje o referencias técnicas adaptadas en {campo}; revisar.")
    for node in data["nodos"]:
        node["evidencia"] = fragmentos.get(node["evidencia"], node["evidencia"])
        node["texto"] = texto_claro(node["texto"])
    if any(len(node["texto"]) > 26 or INDICADOR.search(node["texto"]) for node in data["nodos"]):
        data["nodos"], data["visual"], data["evidencia_relacion"] = [], "resumen", ""
        ajustes.append("El visual técnico se sustituyó por mapa neutral para no recortar etiquetas.")
    for accion in data["acciones"]:
        accion["evidencia"] = fragmentos.get(accion["evidencia"], accion["evidencia"])
        if INDICADOR.search(accion["texto"]) or re.search(r"\b(logs?|IOC|C2|screening|SHA-?256)\b", accion["texto"], re.IGNORECASE):
            accion.update(texto="Consulta el informe con tu equipo de seguridad para comprobar qué medidas son aplicables.", orientacion_general=True, evidencia="")
            ajustes.append("Una tarea técnica se remitió al informe en lugar de presentarla como guía general.")
        accion["texto"] = texto_claro(accion["texto"])
        if accion["orientacion_general"] and accion["texto"] not in {
                *CONSULTAS.values(), *CONSULTAS_ADICIONALES}:
            # Orientación editorial, no un control técnico añadido sin respaldo.
            accion["texto"] = CONSULTAS[accion["rol"]]
            accion["evidencia"] = ""
            ajustes.append("Una orientación general se sustituyó por consulta prudente; revisar su utilidad.")
    # El caption público no reutiliza una redacción libre que pueda contradecir
    # la temporalidad del carrusel. El original permanece en borrador_editorial.
    data["caption"] = caption_temporal(EditorialAlerta.model_validate(data))
    if data["caption"] != e.caption:
        ajustes.append("Caption reconstruido con temporalidad, hecho documentado y límite; revisar.")
    # Evita repetir consultas idénticas después de remitir tareas técnicas.
    unicas = []
    for accion in data["acciones"]:
        if accion["orientacion_general"] and any(
                a["orientacion_general"] and a["rol"] == accion["rol"] for a in unicas):
            ajustes.append("Consultas del mismo público agrupadas; no se rellenan tarjetas repetidas.")
            continue
        if not any((a["rol"], a["texto"].casefold()) == (accion["rol"], accion["texto"].casefold()) for a in unicas):
            unicas.append(accion)
    data["acciones"] = unicas
    if not any(a["rol"] == "personas" for a in data["acciones"]):
        data["acciones"] = [{"rol": "personas", "texto": "Consulta la fuente o al proveedor para comprobar si esta noticia te afecta.",
                             "orientacion_general": True, "evidencia": ""}, *data["acciones"][:2]]
        ajustes.append("Se añadió orientación para personas; otras medidas siguen en el borrador técnico.")
    # La llamada a la acción pública comienza por la persona, no por un permiso de administración.
    data["acciones"].sort(key=lambda a: a["rol"] != "personas")
    return EditorialAlerta.model_validate(data), ajustes


def errores_editoriales(e: EditorialAlerta, fuente: str) -> list[str]:
    errores = []
    if e.tipo_noticia == "riesgo_operativo" and not any(not a.orientacion_general for a in e.acciones):
        errores.append("editorial: riesgo operativo necesita al menos una medida concreta respaldada; no rellenes con consultas. Si falta respaldo, requiere revisión")
    if any(not cita_presente(cita, fuente) for cita in e.evidencias):
        errores.append("editorial.evidencias: aporta citas literales de la fuente, de 10–300 caracteres")
    if e.temporalidad == "historica" and not cita_presente(e.evidencia_temporal, fuente):
        errores.append("editorial: contexto histórico requiere evidencia temporal literal")
    if not any(a.rol == "personas" for a in e.acciones):
        errores.append("editorial: incluye al menos una acción accesible a personas sin administrar redes")
    for accion in e.acciones:
        if accion.orientacion_general and accion.texto not in {*CONSULTAS.values(), *CONSULTAS_ADICIONALES}:
            errores.append("editorial.acciones: orientación general debe ser una consulta prudente del catálogo, no una tarea técnica sin respaldo")
        if not accion.orientacion_general and not cita_presente(accion.evidencia, fuente):
            errores.append("editorial: una medida específica requiere evidencia literal; si no puedes citarla, usa orientación general como consultar el aviso o pedir ayuda al proveedor")
        elif not accion.orientacion_general and not respaldo_accion(accion.texto, accion.evidencia):
            errores.append("editorial: la cita de la medida debe recomendar explícitamente el mismo control; una descripción del ataque no basta. Usa orientación de consulta si no hay respaldo verificable")
    if e.temporalidad == "historica" and re.search(
            r"\b(?:actualmente|hoy|sigue[n]? activ[ao]s?|está[n]? siendo|está[n]? explotando)\b",
            " ".join([e.hecho, e.resumen, e.detalle]), re.IGNORECASE):
        errores.append("editorial: un caso histórico no debe afirmar actividad actual en hecho, resumen o detalle")
    visible = " ".join([e.gancho, e.resumen, e.hecho, e.alcance, e.limite, e.detalle, e.caption,
                        *(a.texto for a in e.acciones), *(n.texto for n in e.nodos)])
    if re.search(r"\b[0-9a-f]{32,64}\b|\[\.\]|\b(?:\d{1,3}\.){3}\d{1,3}\b|\b(?:[a-z0-9-]+\.)+(?:com|net|org|io|xyz|ru|cn|info)\b", visible, re.IGNORECASE):
        errores.append("editorial: lleva hashes e indicadores de red al recurso técnico, no al carrusel")
    jerga = re.search(r"\b(IOC|C2|SHA-?256|screening|payload|jailers?)\b|Ad server\s*[-=]>|\blogs?\b", visible, re.IGNORECASE)
    if jerga:
        errores.append(f"editorial: reemplaza jerga visible ({jerga.group(0)}) por lenguaje accesible; conserva ese dato solo en dato_tecnico")
    for fecha in set(re.findall(r"\b(?:19|20)\d{2}\b", visible)):
        if fecha not in fuente:
            errores.append(f"editorial: el año {fecha} no está en la fuente")
    if not e.caption.rstrip().endswith("?"):
        errores.append("editorial.caption debe terminar con una pregunta")
    return errores


def visual_editorial(e: EditorialAlerta, fuente: str) -> dict:
    """Una selección visual sin evidencia cae en resumen; no inventa una cadena."""
    if (e.visual in {"cadena", "comparacion"} and 2 <= len(e.nodos) <= 3
            and cita_presente(e.evidencia_relacion, fuente)
            and all(cita_presente(n.evidencia, fuente) for n in e.nodos)):
        return {"tipo": "editorial", "clase": e.visual, "nodos": [n.texto for n in e.nodos]}
    return {"tipo": "editorial", "clase": "resumen", "nodos": []}
