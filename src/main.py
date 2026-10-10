import os
from dotenv import load_dotenv
from google import genai

# Carga las variables del archivo .env
load_dotenv()

# Inicializa el cliente (detectará automáticamente GEMINI_API_KEY)
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Hola, probando la conexión con mi archivo .env",
)

print(response.text)