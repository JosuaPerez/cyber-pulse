from playwright.sync_api import sync_playwright

html_logo = """
<!DOCTYPE html>
<html lang="es">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#070B14] flex items-center justify-center h-screen m-0 overflow-hidden">
    <div class="w-[800px] h-[800px] bg-white rounded-full flex items-center justify-center text-slate-900 shadow-[0_0_80px_rgba(255,255,255,0.15)]">
        <svg class="w-[450px] h-[450px]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12h-4l-3-9l-5 18l-3-9H2"></path>
        </svg>
    </div>
</body>
</html>
"""

with sync_playwright() as p:
    print("🎨 Generando nueva foto de perfil...")
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1080, "height": 1080})
    page = context.new_page()
    
    page.set_content(html_logo)
    # Pausa breve para que Tailwind cargue y aplique los estilos por CDN
    page.wait_for_timeout(1500)
    
    page.screenshot(path="foto_perfil_cyberpulse.png")
    print("✅ Logo guardado como foto_perfil_cyberpulse.png")
    browser.close()