import urllib.parse
import json
from playwright.sync_api import sync_playwright

from app import config

def generar_imagenes_carrusel(datos_ia):
    """Mapea el JSON de la IA y toma 5 capturas en el frontend de Vite."""
    config.IMAGENES_DIR.mkdir(parents=True, exist_ok=True)
    base_url = f"{config.TEMPLATES_BASE_URL}/"
    archivos_generados = []
    severidad = datos_ia.get("meta", {}).get("severidad", "critical")
    
    # Mapeo exacto de los datos generados por Gemini a las propiedades de tu React Component
    slides_config = [
        {
            "type": "cover",
            "level": severidad,
            "category": "ALERTA CYBERPULSE",
            "title": datos_ia['slide_1']['title'],
            "description": datos_ia['slide_1']['description']
        },
        {
            "type": "problem",
            "level": severidad,
            "category": "EL PROBLEMA",
            "title": "Contexto de la Amenaza",
            "description": datos_ia['slide_2']['description']
        },
        {
            "type": "detail",
            "level": severidad,
            "category": "ANÁLISIS TÉCNICO",
            "title": "Bajo la Lupa",
            "description": datos_ia['slide_3']['description']
        },
        {
            "type": "impact",
            "level": severidad,
            "category": "EVALUACIÓN",
            "title": "Impacto y Riesgos",
            "description": datos_ia['slide_4']['description'],
            "summary": json.dumps(datos_ia['slide_4']['points'])
        },
        {
            "type": "mitigation",
            "level": severidad,
            "category": "DEFENSA",
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