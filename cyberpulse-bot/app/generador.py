import urllib.parse
import json
from playwright.sync_api import sync_playwright

from app import config

def generar_imagenes_carrusel(datos_ia):
    """Mapea el JSON de la IA y toma 5 capturas en el frontend de Vite."""
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
    if es_cheatsheet:
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
                "category": "RECUERDA",
                "title": "Qué debes recordar",
                "summary": json.dumps(datos_ia.get("tip_bullets", []), ensure_ascii=False),
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
            slide_config['currentSlide'] = idx + 1
            slide_config['totalSlides'] = len(slides_config)
            
            query_string = urllib.parse.urlencode(slide_config)
            page.goto(f"{base_url}?{query_string}", wait_until="domcontentloaded")
            
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            
            # AQUÍ ESTÁ LA MAGIA: Guardamos la ruta completa en la variable
            ruta_completa = config.IMAGENES_DIR / f"slide_{idx + 1}.png"
            
            # Usamos la variable para guardar la foto
            page.screenshot(path=ruta_completa, full_page=True)
            
            # Usamos LA MISMA variable para la lista que irá a Twitter
            archivos_generados.append(ruta_completa)
            
            print(f"📸 Renderizada exitosamente: {ruta_completa} (Tipo: {slide_config['type']})")

        browser.close()

    return archivos_generados