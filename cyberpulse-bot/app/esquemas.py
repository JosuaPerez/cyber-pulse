"""Esquema de salida de Gemini + conversión al formato que ya consumen
generador.py (slides) y publicador_x.py (hilo)."""
import re
from typing import Literal

from pydantic import BaseModel, model_validator

# Límites de longitud (caracteres). Se usan en la validación Y en el prompt,
# así nunca se desincronizan.
LIMITES = {
    "portada_titulo": 50,
    "portada_subtitulo": 110,
    "problema": 320,
    "dato_tecnico": 220,
    "riesgo": 90,       # por punto
    "mitigacion": 100,  # por punto
    "caption": 1000,
    "tweet": 225,       # deja margen para el enlace (23) y emojis (cuentan doble)
}

PATRON_CVE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
PATRON_HASHTAG = re.compile(r"^#\w{2,30}$")


class AnalisisIA(BaseModel):
    """Todos los campos son obligatorios (sin valores por defecto) para que el
    esquema sea compatible con la salida estructurada de Gemini. Si la noticia
    no es relevante, el modelo deja textos vacíos y listas vacías."""

    es_relevante: bool
    motivo_descarte: str
    severidad: Literal["critical", "high", "medium"]
    estado_explotacion: Literal["explotacion_activa", "exploit_publico", "sin_evidencia", "desconocido"]
    cves: list[str]
    portada_titulo: str
    portada_subtitulo: str
    problema: str
    dato_tecnico: str
    riesgos: list[str]
    mitigacion: list[str]
    caption: str
    hashtags: list[str]
    hilo_x: list[str]

    @model_validator(mode="after")
    def validar_contenido(self):
        if not self.es_relevante:
            if not self.motivo_descarte.strip():
                raise ValueError("motivo_descarte no puede estar vacío si es_relevante es false")
            return self

        errores: list[str] = []

        def largo(nombre: str, valor: str, limite: int) -> None:
            v = valor.strip()
            if not v:
                errores.append(f"{nombre} está vacío")
            elif len(v) > limite:
                errores.append(f"{nombre} tiene {len(v)} caracteres (máximo {limite})")

        largo("portada_titulo", self.portada_titulo, LIMITES["portada_titulo"])
        largo("portada_subtitulo", self.portada_subtitulo, LIMITES["portada_subtitulo"])
        largo("problema", self.problema, LIMITES["problema"])
        largo("dato_tecnico", self.dato_tecnico, LIMITES["dato_tecnico"])
        largo("caption", self.caption, LIMITES["caption"])
        if "#" in self.caption:
            errores.append("caption no debe incluir hashtags (van en el campo hashtags)")

        if len(self.riesgos) != 3:
            errores.append("riesgos debe tener exactamente 3 puntos")
        for i, r in enumerate(self.riesgos, 1):
            largo(f"riesgos[{i}]", r, LIMITES["riesgo"])

        if len(self.mitigacion) != 3:
            errores.append("mitigacion debe tener exactamente 3 puntos")
        for i, m in enumerate(self.mitigacion, 1):
            largo(f"mitigacion[{i}]", m, LIMITES["mitigacion"])

        if len(self.hilo_x) != 3:
            errores.append("hilo_x debe tener exactamente 3 tweets")
        for i, t in enumerate(self.hilo_x, 1):
            largo(f"hilo_x[{i}]", t, LIMITES["tweet"])

        if not 3 <= len(self.hashtags) <= 5:
            errores.append("hashtags debe tener entre 3 y 5 elementos")
        for h in self.hashtags:
            if not PATRON_HASHTAG.match(h):
                errores.append(f"hashtag inválido: {h!r} (formato #Palabra, sin espacios)")

        cves_ok = []
        for c in self.cves:
            if PATRON_CVE.fullmatch(c.strip()):
                cves_ok.append(c.strip().upper())
            else:
                errores.append(f"CVE con formato inválido: {c!r}")
        self.cves = cves_ok

        if errores:
            raise ValueError("; ".join(errores))
        return self


def a_formato_legacy(a: AnalisisIA, fuente_nombre: str, fuente_url: str) -> dict:
    """Convierte el análisis validado al dict que ya esperan generador.py y
    publicador_x.py (slide_1..slide_5, caption). La atribución de la fuente
    la agrega el código, no el modelo, para que nunca falte ni se invente."""
    caption = f"{a.caption.strip()}\n\nFuente: {fuente_nombre}\n\n{' '.join(a.hashtags)}"
    hilo = [t.strip() for t in a.hilo_x]
    hilo[-1] = f"{hilo[-1]}\n\nFuente: {fuente_url}"
    return {
        "slide_1": {"title": a.portada_titulo.strip(), "description": a.portada_subtitulo.strip()},
        "slide_2": {"description": a.problema.strip()},
        "slide_3": {"description": a.dato_tecnico.strip()},
        "slide_4": {"description": "Principales riesgos", "points": [r.strip() for r in a.riesgos]},
        "slide_5": {"description": "Cómo protegerse", "points": [m.strip() for m in a.mitigacion]},
        "caption": caption,
        "hilo_x": hilo,
        "meta": {
            "severidad": a.severidad,
            "estado_explotacion": a.estado_explotacion,
            "cves": a.cves,
            "fuente_nombre": fuente_nombre,
            "fuente_url": fuente_url,
        },
    }
