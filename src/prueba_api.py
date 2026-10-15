import os
from dotenv import load_dotenv
from google import genai

# Carga las variables del archivo .env
load_dotenv()

print(os.getenv("GEMINI_API_KEY") is not None)

# Inicializa el cliente (detectará automáticamente GEMINI_API_KEY)
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Hola, probando la conexión con mi archivo .env",
)

print(response.text)