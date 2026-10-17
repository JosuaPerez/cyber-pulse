"""Pruebas visuales ficticias del contrato común; sin IA, red editorial ni publicación."""

import argparse
import json
from pathlib import Path

from PIL import Image

from app import config
from app.editorial_alertas import EditorialAlerta
from app.generador import generar_imagenes_carrusel

ROOT = Path(__file__).resolve().parents[1]


def muestra(tema, clase, stress=False):
    data = json.loads((ROOT / "content/alerts/editorial-demo.json").read_text(encoding="utf-8"))
    e = {
        "gancho": f"¿Qué cambia con este {tema}?", "resumen": "Ejemplo ficticio para revisar el diseño. No describe una amenaza real.",
        "audiencia": "mixta", "hecho": "Se muestra una demostración ficticia de diseño, no un incidente real.", "alcance": "Esta demostración muestra cómo separar el público y las condiciones del caso sin afirmar que todos estén afectados.",
        "limite": "No es una alerta real ni una comprobación de tu equipo.",
        "temporalidad": "vigencia_no_confirmada", "evidencia_temporal": "", "detalle": "El hallazgo se explica con lenguaje accesible. Los identificadores técnicos quedan en el recurso de referencia.",
        "acciones": [{"rol": "personas", "texto": "Consulta la fuente antes de asumir que el caso te afecta.", "orientacion_general": True, "evidencia": ""},
                     {"rol": "administradores", "texto": "Revisa el alcance del aviso y confirma qué medidas corresponden.", "orientacion_general": True, "evidencia": ""},
                     {"rol": "personas", "texto": "Pregunta al proveedor si necesitas ayuda para comprobar tu situación.", "orientacion_general": True, "evidencia": ""}],
        "caption": "Demostración de diseño, no una amenaza real. ¿Se entiende el siguiente paso?",
        "evidencias": ["Demostración ficticia del contrato común."], "visual": clase,
        "nodos": [], "evidencia_relacion": ""}
    if clase != "resumen":
        labels = ["Contenido inicial", "Selección del objetivo", "Posible impacto"] if clase == "cadena" else ["Aviso publicado", "Entorno por comprobar"]
        e["nodos"] = [{"texto": label, "evidencia": "Demostración ficticia del contrato común."} for label in labels]
    if tema == "riesgo-operativo":
        e.update(tipo_noticia="riesgo_operativo", gancho="¿Qué IA usa tu equipo para trabajar?",
                 resumen="Ejemplo ficticio: revisar cuentas, herramientas y políticas de uso de IA en el trabajo.",
                 hecho="Se ilustra una práctica de trabajo, no una brecha ni un incidente confirmado.",
                 alcance="Sirve para revisar qué cuentas y herramientas usa el equipo y qué reglas se aplican a la información de trabajo.",
                 detalle="El ejemplo organiza la revisión en personas, herramientas y políticas. No evalúa a ninguna empresa ni recomienda un producto.",
                 limite="Es una demostración ficticia, no evidencia de exposición de datos.",
                 acciones=[{"rol": "personas", "texto": "Comprueba con tu equipo qué herramientas están aprobadas para el trabajo.", "orientacion_general": False, "evidencia": "Demostración ficticia, no recomendación de una noticia."}])
    if stress:
        for key, length in [("gancho", 50), ("resumen", 110), ("hecho", 110), ("alcance", 240), ("limite", 100), ("detalle", 180)]:
            e[key] = ("Texto largo de prueba " * 20)[:length]
        for action in e["acciones"]:
            action["texto"] = ("Consulta el contexto de esta demostración " * 5)[:90]
    validated = EditorialAlerta.model_validate(e)
    data["meta"].update({"editorial": validated.model_dump(), "editorial_version": 2,
                         "fuente_nombre": "DEMOSTRACIÓN FICTICIA", "fuente_url": "https://example.invalid/demo",
                         "visual_apoyo": {"tipo": "editorial", "clase": clase, "nodos": [n.texto for n in validated.nodos]}})
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stress", action="store_true")
    parser.add_argument("--tema", choices=["aviso", "incidente", "ataque", "riesgo-operativo"])
    args = parser.parse_args()
    original = config.IMAGENES_DIR
    try:
        for tema, clase in [("aviso", "resumen"), ("incidente", "comparacion"), ("ataque", "cadena"), ("riesgo-operativo", "resumen")]:
            if args.tema and tema != args.tema:
                continue
            output = ROOT / "media/editorial-universal" / (tema + ("-limites" if args.stress else ""))
            config.IMAGENES_DIR = output
            paths = generar_imagenes_carrusel(muestra(tema, clase, args.stress), variante_alerta="clara")
            sheet = Image.new("RGB", (1080, 1350), "#080f20")
            for i, path in enumerate(paths):
                with Image.open(path) as rendered:
                    sheet.paste(rendered.resize((540, 675), Image.Resampling.LANCZOS), (i % 2 * 540, i // 2 * 675))
            sheet.save(output / "carousel.png")
            print(output / "carousel.png")
    finally:
        config.IMAGENES_DIR = original


if __name__ == "__main__":
    main()
