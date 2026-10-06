import os
from playwright.sync_api import sync_playwright

def generar_banner_x():
    print("🎨 Generando el banner para X...")
    
    html_banner = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
            body {
                font-family: 'Fira Code', monospace;
                background-color: #070B14; /* El azul muy oscuro de tus carruseles */
                margin: 0;
                overflow: hidden;
            }
            .glow-text {
                text-shadow: 0 0 10px rgba(239, 68, 68, 0.7); /* Brillo rojo CyberPulse */
            }
            .grid-bg {
                background-image: 
                    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
                background-size: 30px 30px;
            }
        </style>
    </head>
    <body class="w-[1500px] h-[500px] relative flex items-center grid-bg">
        
        <!-- Elemento de fondo: Código abstracto difuminado -->
        <div class="absolute inset-0 opacity-10 text-green-500 text-sm overflow-hidden p-8 pointer-events-none z-0 select-none">
             const exploit = await scanner.detect({ payload: 'CVE-2026-X', target: 'infrastructure' });<br>
             if (exploit.critical) { initProtocol(override); }<br>
             // MONITORING ACTIVE...<br>
             SYS.LOG: UNAUTHORIZED ACCESS ATTEMPT BLOCKED.
        </div>

        <!-- Contenedor Principal (Simulando una Terminal) -->
        <div class="z-10 ml-20 mt-8 w-2/3 border border-red-500/30 bg-black/60 rounded-xl p-8 backdrop-blur-sm shadow-[0_0_30px_rgba(239,68,68,0.15)] relative overflow-hidden">
            
            <!-- Barra superior de la terminal -->
            <div class="absolute top-0 left-0 w-full h-8 bg-black/80 border-b border-red-500/30 flex items-center px-4 space-x-2">
                <div class="w-3 h-3 rounded-full bg-red-500"></div>
                <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div class="w-3 h-3 rounded-full bg-green-500"></div>
                <span class="ml-4 text-gray-500 text-xs">root@cyberpulse:~#</span>
            </div>

            <div class="mt-8">
                <div class="flex items-center space-x-4 mb-2">
                    <!-- Ícono de Pulso (similar al de tu logo) -->
                    <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-slate-900 shadow-[0_0_10px_rgba(255,255,255,0.3)]">
                         <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12h-4l-3-9l-5 18l-3-9H2"></path>
                        </svg>
                    </div>
                    <h1 class="text-white text-6xl font-bold tracking-wider uppercase">CyberPulse</h1>
                </div>
                
                <p class="text-red-400 text-xl font-bold mt-4 glow-text">> INICIANDO ESCANEO DE AMENAZAS...</p>
                
                <div class="mt-6 text-gray-300 text-lg space-y-2">
                    <p><span class="text-green-500">✔</span> Monitorizando feeds globales 24/7</p>
                    <p><span class="text-green-500">✔</span> Analizando vulnerabilidades Zero-Day</p>
                    <p><span class="text-green-500">✔</span> Sintetizando inteligencia técnica</p>
                    <p class="animate-pulse text-gray-500 mt-4">_Esperando siguiente evento...</p>
                </div>
            </div>
        </div>

        <!-- Detalles decorativos lado derecho -->
        <div class="absolute right-20 bottom-16 flex flex-col items-end opacity-50">
            <div class="flex space-x-2 mb-2">
                <div class="w-8 h-2 bg-red-500"></div>
                <div class="w-4 h-2 bg-red-500"></div>
                <div class="w-16 h-2 bg-red-500"></div>
            </div>
            <p class="text-red-500 text-sm">SEC-OPS // AUTOMATED</p>
        </div>

    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1500x500 es la medida oficial del banner de X
        context = browser.new_context(viewport={"width": 1500, "height": 500})
        page = context.new_page()
        page.set_content(html_banner)
        
        page.wait_for_timeout(1000) # Tiempo para que renderice
        
        page.screenshot(path="banner_x.png", full_page=True)
        print("✅ Banner guardado exitosamente como 'banner_x.png'")
        
        context.close()
        browser.close()

if __name__ == "__main__":
    generar_banner_x()