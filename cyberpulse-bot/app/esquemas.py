"""Esquema de salida de Gemini + conversión al formato que ya consumen
generador.py (slides) y publicador_x.py (hilo)."""
import re
from typing import Literal

from pydantic import BaseModel, model_validator
from app.editorial_alertas import EditorialAlerta
from app.alertas_v3 import AnalisisAlerta as AnalisisAlerta  # contrato nuevo; AnalisisIA queda para educativos

# Límites de longitud (caracteres). Se usan en la validación Y en el prompt,
# así nunca se desincronizan.
LIMITES = {
    "portada_titulo": 50,
    "portada_subtitulo": 110,
    "problema": 320,
    "dato_tecnico": 220,
    "sintaxis": 120,
    "explicacion_item": 90,
    "paso": 100,
    "tip_texto": 110,
    "chip": 15,
    "stat_valor": 10,
    "stat_etiqueta": 20,
    "tip_bullet": 60,
    "riesgo": 90,       # por punto
    "mitigacion": 100,  # por punto
    "caption": 1000,
    "tweet": 225,       # deja margen para el enlace (23) y emojis (cuentan doble)
}

PATRON_CVE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
PATRON_HASHTAG = re.compile(r"^#\w{2,30}$")


class ItemCheatsheet(BaseModel):
    sintaxis: str
    explicacion: str


class ItemChecklist(BaseModel):
    paso: str


class ChipTip(BaseModel):
    texto: str


class StatBlock(BaseModel):
    valor: str
    etiqueta: str


class SlideTip(BaseModel):
    texto: str
    chips: list[ChipTip]
    stats: list[StatBlock]


class AnalisisIA(BaseModel):
    """Los campos editoriales son obligatorios. Los enriquecimientos opcionales
    conservan compatibilidad con análisis anteriores. Si la noticia no es
    relevante, el modelo deja textos vacíos y listas vacías."""

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
    visual_tipo: Literal["none", "vm_isolation"] = "none"
    visual_evidencia: str = ""
    editorial: EditorialAlerta | None = None
    items: list["ItemCheatsheet"] | None = None
    items_checklist: list["ItemChecklist"] | None = None
    tip_slides: list["SlideTip"] | None = None
    tip_bullets: list[str] | None = None
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

        tip_presente = self.tip_slides is not None or self.tip_bullets is not None
        if tip_presente:
            if self.tip_slides is None or self.tip_bullets is None:
                errores.append("tip_slides y tip_bullets deben aparecer juntos")
            elif len(self.tip_slides) != 2:
                errores.append("tip_slides debe tener exactamente 2 elementos")
            else:
                for i, slide in enumerate(self.tip_slides, 1):
                    largo(f"tip_slides[{i}].texto", slide.texto, LIMITES["tip_texto"])
                    if not 2 <= len(slide.chips) <= 4:
                        errores.append(f"tip_slides[{i}].chips debe tener entre 2 y 4 elementos")
                    for j, chip in enumerate(slide.chips, 1):
                        largo(
                            f"tip_slides[{i}].chips[{j}].texto",
                            chip.texto,
                            LIMITES["chip"],
                        )
                    if not 2 <= len(slide.stats) <= 3:
                        errores.append(f"tip_slides[{i}].stats debe tener entre 2 y 3 elementos")
                    for j, stat in enumerate(slide.stats, 1):
                        largo(
                            f"tip_slides[{i}].stats[{j}].valor",
                            stat.valor,
                            LIMITES["stat_valor"],
                        )
                        largo(
                            f"tip_slides[{i}].stats[{j}].etiqueta",
                            stat.etiqueta,
                            LIMITES["stat_etiqueta"],
                        )
            if self.tip_bullets is not None:
                if not 3 <= len(self.tip_bullets) <= 4:
                    errores.append("tip_bullets debe tener entre 3 y 4 elementos")
                for i, bullet in enumerate(self.tip_bullets, 1):
                    largo(f"tip_bullets[{i}]", bullet, LIMITES["tip_bullet"])
            if (
                self.items is not None
                or self.items_checklist is not None
                or self.riesgos
                or self.mitigacion
            ):
                errores.append(
                    "el formato tip no puede combinarse con items, items_checklist, riesgos o mitigacion"
                )
        elif self.items is not None and self.items_checklist is not None:
            errores.append("items e items_checklist no pueden usarse a la vez")
        elif self.items_checklist is not None:
            if not 4 <= len(self.items_checklist) <= 6:
                errores.append("items_checklist debe tener entre 4 y 6 pasos")
            for i, item in enumerate(self.items_checklist, 1):
                largo(f"items_checklist[{i}].paso", item.paso, LIMITES["paso"])
        elif self.items is None:
            if len(self.riesgos) != 3:
                errores.append("riesgos debe tener exactamente 3 puntos")
            for i, r in enumerate(self.riesgos, 1):
                largo(f"riesgos[{i}]", r, LIMITES["riesgo"])

            if len(self.mitigacion) != 3:
                errores.append("mitigacion debe tener exactamente 3 puntos")
            for i, m in enumerate(self.mitigacion, 1):
                largo(f"mitigacion[{i}]", m, LIMITES["mitigacion"])
        else:
            if not 3 <= len(self.items) <= 4:
                errores.append("items debe tener entre 3 y 4 elementos")
            for i, item in enumerate(self.items, 1):
                largo(f"items[{i}].sintaxis", item.sintaxis, LIMITES["sintaxis"])
                largo(
                    f"items[{i}].explicacion",
                    item.explicacion,
                    LIMITES["explicacion_item"],
                )

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
            "familia": "alerta",
            "severidad": a.severidad,
            "estado_explotacion": a.estado_explotacion,
            "cves": a.cves,
            "fuente_nombre": fuente_nombre,
            "fuente_url": fuente_url,
        },
    }
