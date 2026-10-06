import edge_tts
import asyncio

async def generar_audio_asincrono(texto, ruta_salida):
   
    # Puedes ajustar el 'rate' para que hable un poco más rápido si quieres que suene más urgente
    comunicador = edge_tts.Communicate(texto, "es-CO-GonzaloNeural", rate="+10%")
    await comunicador.save(ruta_salida)

def crear_audio_reel(texto_guion, ruta_salida="media/videos/reel_audio.mp3"):
    """Función de envoltura para poder llamarla fácilmente desde el bot principal."""
    print("🎙️ Grabando voz en off para el Reel...")
    asyncio.run(generar_audio_asincrono(texto_guion, ruta_salida))
    print(f"✅ Audio guardado exitosamente en: {ruta_salida}")

# Bloque de prueba
if __name__ == "__main__":
    guion_prueba = "¡Alerta Zero-Day! Atacantes están explotando una vulnerabilidad crítica en servidores de Check Point. Si no parchas hoy, tu red podría ser la siguiente. Tienes todos los detalles técnicos y la estrategia de mitigación en nuestro último post. Protege tu infraestructura ahora."
    crear_audio_reel(guion_prueba)