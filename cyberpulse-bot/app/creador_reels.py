import os
import glob
from playwright.sync_api import sync_playwright
from moviepy import VideoFileClip, AudioFileClip

def grabar_animacion_base(duracion_segundos):
    print(f"🎥 Grabando video base de {duracion_segundos} segundos...")
    
    # Un diseño vertical agresivo usando Tailwind
    html_reel = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @keyframes pulse-glow {
                0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.2); }
                50% { box-shadow: 0 0 60px rgba(239, 68, 68, 0.8); }
            }
            .radar-box { animation: pulse-glow 2s infinite; }
            @keyframes scroll-code {
                0% { transform: translateY(0); }
                100% { transform: translateY(-50%); }
            }
            .code-scroll { animation: scroll-code 10s linear infinite; }
        </style>
    </head>
    <body class="bg-[#070B14] flex flex-col items-center justify-center h-screen m-0 overflow-hidden text-white font-mono relative">
        <div class="absolute inset-0 opacity-10 text-green-500 text-xs overflow-hidden">
            <div class="code-scroll p-4">
                01010011 01011001 01010011 01010100 01000101 01001101 00100000 01000110 01000001 01001001 01001100 <br>
                EXPLOIT DETECTED // PAYLOAD INJECTED // BYPASSING FIREWALL...<br>
                01000011 01010010 01001001 01010100 01001001 01000011 01000001 01001100 00100000 01000101 01010010 01010010 01001111 01010010 <br>
                INITIATING OVERRIDE PROTOCOL... ACCESS GRANTED.<br>
                (Repite estas líneas mentalmente para llenar el fondo)
            </div>
        </div>

        <div class="z-10 radar-box border border-red-500/50 bg-black/50 p-12 rounded-3xl flex flex-col items-center w-4/5">
            <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center text-slate-900 shadow-[0_0_15px_rgba(255,255,255,0.4)] mb-8">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 12h-4l-3-9l-5 18l-3-9H2"></path>
                </svg>
            </div>
            <h1 class="text-red-500 text-4xl font-bold mb-4 tracking-widest">ALERTA CRÍTICA</h1>
            <p class="text-xl text-center text-gray-300">Escucha el reporte completo...</p>
            
            <div class="mt-12 flex space-x-2">
                <div class="w-3 h-12 bg-red-500 animate-bounce" style="animation-delay: 0s"></div>
                <div class="w-3 h-16 bg-red-500 animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-3 h-10 bg-red-500 animate-bounce" style="animation-delay: 0.2s"></div>
                <div class="w-3 h-14 bg-red-500 animate-bounce" style="animation-delay: 0.3s"></div>
                <div class="w-3 h-8 bg-red-500 animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
        </div>
    </body>
    </html>
    """
    
    os.makedirs("temp_video", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Formato exacto de Reels: 1080x1920
        context = browser.new_context(
            viewport={"width": 1080, "height": 1920},
            record_video_dir="media/videos/temp_video/"
        )
        page = context.new_page()
        page.set_content(html_reel)
        
        # Esperamos el tiempo que dure el audio + 1 segundo de margen
        page.wait_for_timeout((duracion_segundos + 1) * 1000)
        
        context.close()
        browser.close()
        
        # Playwright guarda el video con un nombre aleatorio (.webm), buscamos el más reciente
        lista_videos = glob.glob('temp_video/*.webm')
        ultimo_video = max(lista_videos, key=os.path.getctime)
        return ultimo_video

def ensamblar_reel(ruta_audio, ruta_salida="reel_cyberpulse.mp4"):
    print("🎬 Sincronizando audio y video en el estudio de edición...")
    
    # 1. Cargamos el audio
    audio = AudioFileClip(ruta_audio)
    duracion_audio = audio.duration
    
    # 2. Grabamos el video silencioso con Playwright
    ruta_video_base = grabar_animacion_base(duracion_audio)
    
    # 3. Ensamblamos todo
    video = VideoFileClip(ruta_video_base)
    
    # ACTUALIZACIÓN MOVIEPY 2.0: subclip -> subclipped y set_audio -> with_audio
    video = video.subclipped(0, duracion_audio)
    video_final = video.with_audio(audio)
    
    # 4. Exportamos en MP4 con el codec que le gusta a Instagram
    video_final.write_videofile(
        ruta_salida, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac",
        logger=None # Para mantener la terminal limpia
    )
    
    print(f"✅ ¡Reel finalizado con éxito! Guardado como: {ruta_salida}")
    
    # Limpieza: borramos el video temporal
    video.close()
    audio.close()
    os.remove(ruta_video_base)

if __name__ == "__main__":
    # Asegúrate de tener tu archivo 'reel_audio.mp3' en la misma carpeta antes de correr esto
    if os.path.exists("reel_audio.mp3"):
        ensamblar_reel("reel_audio.mp3")
    else:
        print("❌ No se encontró 'reel_audio.mp3'. Genera el audio primero.")