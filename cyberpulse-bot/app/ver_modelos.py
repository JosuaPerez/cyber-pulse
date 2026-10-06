import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Inicializamos el cliente con tus credenciales
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

print("🔍 Consultando modelos disponibles en tu API Key...\n")

# Iteramos sobre la lista de modelos de tu cuenta
for modelo in client.models.list():
    print(f"- {modelo.name}")