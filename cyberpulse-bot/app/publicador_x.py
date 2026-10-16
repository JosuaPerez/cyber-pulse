import os
import tweepy
from dotenv import load_dotenv

# Cargar las credenciales del .env
load_dotenv()


def indices_imagenes_hilo(cantidad):
    if cantidad == 4:
        return [[0], [1, 2], [3]]
    if cantidad == 5:
        return [[0], [1, 2], [3, 4]]
    raise ValueError("El hilo requiere un carrusel completo de 4 o 5 imágenes")


def publicar_hilo_x(rutas_imagenes, datos_json):
    grupos = indices_imagenes_hilo(len(rutas_imagenes))
    print("🐦 Preparando hilo para X (Twitter)...")
    
    # 1. Extraer credenciales
    consumer_key = os.getenv("CONSUMER_KEY_X")
    consumer_secret = os.getenv("CONSUMER_SECRET_X")
    access_token = os.getenv("ACCESS_TOKEN_X")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET_X")
    
    # 2. Autenticación Dual (API v1.1 para fotos, Client v2 para texto)
    try:
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
        api = tweepy.API(auth)
        
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
    except Exception as e:
        print(f"❌ Error de autenticación en X: {e}")
        return
        
    try:
        # 3. Subir todas las imágenes del carrusel validado.
        print("📤 Subiendo imágenes a X...")
        media_ids = []
        for ruta in rutas_imagenes:
            media = api.media_upload(ruta)
            media_ids.append(media.media_id)
            
        # 4. Preparar el texto de los Tweets a partir del JSON de Gemini
        titulo = datos_json['slide_1']['title']
        desc_corta = datos_json['slide_1']['description']
        
        # TWEET 1 (Gancho + Portada)
        texto_tweet_1 = f"🚨 {titulo}\n\n{desc_corta}\n\n🧵 Sigue el hilo para el análisis técnico 👇 #Ciberseguridad #InfoSec"
        
        # TWEET 2 (Problema y Detalle + Slide 2 y 3)
        texto_tweet_2 = f"🔍 El Problema:\n{datos_json['slide_2']['description']}\n\n⚙️ Dato Técnico:\n{datos_json['slide_3']['description']}"
        
        # TWEET 3 (Riesgos y Soluciones + Slide 4 y 5)
        texto_tweet_3 = f"⚠️ Impacto Principal:\n- {datos_json['slide_4']['points'][0]}\n\n🛡️ Cómo mitigarlo:\n- {datos_json['slide_5']['points'][0]}\n\nMantén tu infraestructura segura. 💻📡"

        # 5. Publicar el Hilo en cascada
        print("📝 Publicando Tweet 1 (Portada)...")
        tweet_1 = client.create_tweet(text=texto_tweet_1, media_ids=[media_ids[i] for i in grupos[0]])
        tweet_1_id = tweet_1.data['id']
        
        print("📝 Publicando Tweet 2 (Análisis)...")
        tweet_2 = client.create_tweet(text=texto_tweet_2, media_ids=[media_ids[i] for i in grupos[1]], in_reply_to_tweet_id=tweet_1_id)
        tweet_2_id = tweet_2.data['id']
        
        print("📝 Publicando Tweet 3 (Mitigación)...")
        client.create_tweet(text=texto_tweet_3, media_ids=[media_ids[i] for i in grupos[2]], in_reply_to_tweet_id=tweet_2_id)
        
        print("✅ ¡Hilo publicado con éxito en la cuenta de X!")
        
    except tweepy.errors.TweepyException as e:
        print(f"❌ Error de la API de X al publicar: {e}")
