import urllib.parse
import json
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

from app import config
from app.editorial_alertas import EditorialAlerta

def visual_apoyo_validado(meta):
    """Acepta datos explícitos revisados; no deduce versiones del título."""
    visual = meta.get("visual_apoyo")
    if isinstance(visual, dict) and visual.get("tipo") == "editorial":
        clase, nodos = visual.get("clase"), visual.get("nodos", [])
        if clase == "resumen":
            return {"tipo": "editorial", "clase": "resumen", "nodos": []}
        if (clase in {"cadena", "comparacion"} and isinstance(nodos, list) and 2 <= len(nodos) <= 3
                and all(isinstance(n, str) and 2 <= len(n.strip()) <= 26 for n in nodos)):
            return {"tipo": "editorial", "clase": clase, "nodos": nodos}
        return {"tipo": "editorial", "clase": "resumen", "nodos": []}
    if isinstance(visual, dict) and visual.get("tipo") == "vm_isolation":
        try:
            source = urllib.parse.urlsplit(meta.get("fuente_url", ""))
            if source.scheme == "https" and source.hostname:
                return {"tipo": "vm_isolation"}
        except (ValueError, TypeError):
            pass
        return {}
    if not isinstance(visual, dict) or visual.get("tipo") != "firefox_version":
        return {}
    version = visual.get("version", "")
    source_url = meta.get("fuente_url", "")
    if not isinstance(source_url, str):
        return {}
    try:
        source = urllib.parse.urlsplit(source_url)
    except ValueError:
        return {}
    if (not isinstance(version, str) or not re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){0,3}", version)
            or source.scheme != "https" or source.hostname not in {"mozilla.org", "www.mozilla.org"}
            or not source.path.startswith("/en-US/security/advisories/")):
        return {}
    return {"tipo": "firefox_version", "version": version}


def parametros_variante_alerta(meta, variante):
    """Variante explícita; no modifica educativos ni infiere datos de la noticia."""
    if variante not in {"clasica", "clara", "editorial"}:
        raise ValueError("La variante de alerta debe ser clasica, clara o editorial")
    if variante == "clasica" or meta.get("familia", "alerta") != "alerta":
        return {}
    return {
        "alertVariant": variante,
        "sourceName": meta.get("fuente_nombre", ""),
        "sourceUrl": meta.get("fuente_url", ""),
        "exploitation": meta.get("estado_explotacion", "desconocido"),
        "cves": json.dumps(meta.get("cves", []), ensure_ascii=False),
        **({"preparedOn": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
            "sourceDate": meta.get("fecha_fuente", ""),
            "editorialData": json.dumps(meta.get("editorial", {}), ensure_ascii=False),
            "supportVisual": json.dumps(visual_apoyo_validado(meta))} if variante == "clara" else {}),
    }


def cantidad_imagenes_esperada(meta, variante=None):
    seleccion = config.ALERTAS_VARIANTE if variante is None else variante
    params = parametros_variante_alerta(meta, seleccion)
    return 4 if params.get("alertVariant") == "clara" else 5


def construir_alerta_clara(datos):
    """Reordena datos validados sin resumir, truncar ni inventar alcance."""
    shared = {"familia": "alerta", "level": datos.get("meta", {}).get("severidad", "medium")}
    editorial = datos.get("meta", {}).get("editorial")
    if editorial:
        e = EditorialAlerta.model_validate(editorial)
        return [
            {**shared, "type": "cover", "title": e.gancho, "description": e.resumen},
            {**shared, "type": "scope", "title": "A quién le concierne", "description": e.hecho},
            {**shared, "type": "context_risks", "title": "Qué sabemos y qué no", "description": e.detalle,
             "summary": json.dumps([], ensure_ascii=False)},
            {**shared, "type": "mitigation", "title": "Qué puedes hacer", "description": "Medidas según tu situación",
             "summary": json.dumps([f"{'Para equipos de TI' if a.rol == 'administradores' else 'Para ti'}: {a.texto}"
                                     for a in e.acciones], ensure_ascii=False)},
        ]
    return [
        {**shared, "type": "cover", "category": "LO IMPORTANTE",
         "title": datos["slide_1"]["title"], "description": datos["slide_1"]["description"]},
        {**shared, "type": "scope", "category": "¿TE AFECTA?", "title": "Qué debes revisar",
         "description": datos["slide_2"]["description"]},
        {**shared, "type": "context_risks", "category": "CONTEXTO Y FUENTE", "title": "El detalle y sus límites",
         "description": datos["slide_3"]["description"],
         "summary": json.dumps(datos["slide_4"]["points"], ensure_ascii=False)},
        {**shared, "type": "mitigation", "category": "QUÉ HACER", "title": "Qué hacer ahora",
         "description": datos["slide_5"]["description"],
         "summary": json.dumps(datos["slide_5"]["points"], ensure_ascii=False)},
    ]


def generar_imagenes_carrusel(datos_ia, *, variante_alerta=None):
    """Mapea el análisis a cuatro alertas claras o cinco slides del formato previo."""
    variante = config.ALERTAS_VARIANTE if variante_alerta is None else variante_alerta
    parametros_variante = parametros_variante_alerta(datos_ia.get("meta", {}), variante)
    config.IMAGENES_DIR.mkdir(parents=True, exist_ok=True)
    base_url = f"{config.TEMPLATES_BASE_URL}/"
    archivos_generados = []
    meta = datos_ia.get("meta", {})
    familia = meta.get("familia", "alerta")
    tipo = meta.get("tipo", "")
    severidad = meta.get("severidad", "critical")
    es_educativo = familia == "educativo"
    es_cheatsheet = es_educativo and tipo == "cheatsheet"
    es_checklist = es_educativo and tipo == "checklist"
    es_tip = es_educativo and tipo == "tip"
    categoria_portada = "CYBERPULSE EDUCA" if es_educativo else "ALERTA CYBERPULSE"
    categorias = (
        ["CONCEPTO", "EN DETALLE", "PUNTOS CLAVE", "APLÍCALO"]
        if es_educativo
        else ["EL PROBLEMA", "ANÁLISIS TÉCNICO", "EVALUACIÓN", "DEFENSA"]
    )
    
    # Mapeo exacto de los datos generados por Gemini a las propiedades de tu React Component
    if parametros_variante.get("alertVariant") == "clara":
        slides_config = construir_alerta_clara(datos_ia)
    elif es_cheatsheet:
        items = datos_ia.get("items", [])
        slides_config = [
            {
                "type": "cover",
                "level": severidad,
                "familia": familia,
                "category": categoria_portada,
                "title": datos_ia["slide_1"]["title"],
                "description": datos_ia["slide_1"]["description"],
            },
            {
                "type": "command_pair",
                "level": severidad,
                "familia": familia,
                "category": "COMANDOS 1-2",
                "title": "Comandos esenciales",
                "summary": json.dumps(items[:2], ensure_ascii=False),
            },
            {
                "type": "command_pair",
                "level": severidad,
                "familia": familia,
                "category": "COMANDOS 3-4",
                "title": "Más comandos útiles",
                "summary": json.dumps(items[2:4], ensure_ascii=False),
            },
            {
                "type": "pro_tip",
                "level": severidad,
                "familia": familia,
                "category": "TIP PRO",
                "title": "Dato pro",
                "description": datos_ia["slide_3"]["description"],
            },
            {
                "type": "recap",
                "level": severidad,
                "familia": familia,
                "category": "RESUMEN COMPLETO",
                "title": "Todos los comandos",
                "summary": json.dumps(items, ensure_ascii=False),
            },
        ]
    elif es_checklist:
        pasos = datos_ia.get("items_checklist", [])
        slides_config = [
            {
                "type": "cover",
                "level": severidad,
                "familia": familia,
                "category": categoria_portada,
                "title": datos_ia["slide_1"]["title"],
                "description": datos_ia["slide_1"]["description"],
            },
            {
                "type": "checklist_steps",
                "level": severidad,
                "familia": familia,
                "category": "VERIFICACIÓN 1-3",
                "title": "Primera revisión",
                "summary": json.dumps(pasos[:3], ensure_ascii=False),
            },
            {
                "type": "checklist_steps",
                "level": severidad,
                "familia": familia,
                "category": "VERIFICACIÓN 4-6",
                "title": "Completa la revisión",
                "summary": json.dumps(pasos[3:], ensure_ascii=False),
            },
            {
                "type": "pro_tip",
                "level": severidad,
                "familia": familia,
                "category": "TIP PRO",
                "title": "Dato pro",
                "description": datos_ia["slide_3"]["description"],
            },
            {
                "type": "checklist_steps",
                "level": severidad,
                "familia": familia,
                "category": "CHECKLIST COMPLETO",
                "title": "Revisión completa",
                "summary": json.dumps(pasos, ensure_ascii=False),
            },
        ]
    elif es_tip:
        tip_slides = datos_ia.get("tip_slides", [])
        slides_config = [
            {
                "type": "cover",
                "level": severidad,
                "familia": familia,
                "category": categoria_portada,
                "title": datos_ia["slide_1"]["title"],
                "description": datos_ia["slide_1"]["description"],
            },
            *[
                {
                    "type": "tip_content",
                    "level": severidad,
                    "familia": familia,
                    "category": f"TIP {indice}",
                    "title": f"Señal clave {indice}",
                    "summary": json.dumps(slide, ensure_ascii=False),
                }
                for indice, slide in enumerate(tip_slides, 1)
            ],
            {
                "type": "tip_bullets",
                "level": severidad,
                "familia": familia,
                "category": "RECUERDA 1-2",
                "title": "Qué debes recordar",
                "summary": json.dumps(datos_ia.get("tip_bullets", [])[:2], ensure_ascii=False),
            },
            {
                "type": "tip_bullets",
                "level": severidad,
                "familia": familia,
                "category": "RECUERDA 3-4",
                "title": "Llévatelo contigo",
                "summary": json.dumps(datos_ia.get("tip_bullets", [])[2:], ensure_ascii=False),
            },
        ]
    else:
        slides_config = [
        {
            "type": "cover",
            "level": severidad,
            "familia": familia,
            "category": categoria_portada,
            "title": datos_ia['slide_1']['title'],
            "description": datos_ia['slide_1']['description']
        },
        {
            "type": "problem",
            "level": severidad,
            "familia": familia,
            "category": categorias[0],
            "title": "Contexto de la Amenaza",
            "description": datos_ia['slide_2']['description']
        },
        {
            "type": "detail",
            "level": severidad,
            "familia": familia,
            "category": categorias[1],
            "title": "Bajo la Lupa",
            "description": datos_ia['slide_3']['description']
        },
        {
            "type": "impact",
            "level": severidad,
            "familia": familia,
            "category": categorias[2],
            "title": "Impacto y Riesgos",
            "description": datos_ia['slide_4']['description'],
            "summary": json.dumps(datos_ia['slide_4']['points'])
        },
        {
            "type": "mitigation",
            "level": severidad,
            "familia": familia,
            "category": categorias[3],
            "title": "Estrategia de Mitigación",
            "description": datos_ia['slide_5']['description'],
            "summary": json.dumps(datos_ia['slide_5']['points'])
        }
        ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1080, "height": 1350})
        page = context.new_page()

        for idx, slide_config in enumerate(slides_config):
            slide_config.update(parametros_variante)
            slide_config['currentSlide'] = idx + 1
            slide_config['totalSlides'] = len(slides_config)
            
            query_string = urllib.parse.urlencode(slide_config)
            page.goto(f"{base_url}?{query_string}", wait_until="domcontentloaded")
            
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            if parametros_variante:
                page.locator(".daily-alert").wait_for()
                overflow = page.evaluate("""() => {
                    const root = document.querySelector('.daily-alert');
                    const body = document.querySelector('.daily-content');
                    return root.scrollHeight > root.clientHeight + 1 ||
                           root.scrollWidth > root.clientWidth + 1 ||
                           body.scrollHeight > body.clientHeight + 1 ||
                           body.scrollWidth > body.clientWidth + 1;
                }""")
                if overflow:
                    raise ValueError(f"La variante {variante} desborda en la diapositiva {idx + 1}")
            
            # AQUÍ ESTÁ LA MAGIA: Guardamos la ruta completa en la variable
            ruta_completa = config.IMAGENES_DIR / f"slide_{idx + 1}.png"
            
            # Usamos la variable para guardar la foto
            page.screenshot(path=ruta_completa, full_page=not bool(parametros_variante))
            
            # Usamos LA MISMA variable para la lista que irá a Twitter
            archivos_generados.append(ruta_completa)
            
            print(f"📸 Renderizada exitosamente: {ruta_completa} (Tipo: {slide_config['type']})")

        browser.close()

    return archivos_generados
