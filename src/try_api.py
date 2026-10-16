import os
import requests
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# --- Responsabilidad 1: Construir la petición (URL y Body) ---
def construir_peticion(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-3.5-flash-lite"  # O el modelo que te exijan en el bootcamp
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }
    return url, body


# --- Responsabilidad 2: Enviar la petición a la API ---
def enviar_peticion(url, body):
    respuesta = requests.post(url, json=body)
    return respuesta.json()


# --- Responsabilidad 3: Extraer el texto de la respuesta ---
def extraer_texto(datos_json):
    if "candidates" not in datos_json:
        return f"Error en la respuesta de la API: {datos_json}"
        
    return datos_json["candidates"][0]["content"]["parts"][0]["text"]


# --- Función Orquestadora (Une las 3 responsabilidades) ---
def test_api_connection(pregunta):
    # 1. Construimos
    url, body = construir_peticion(pregunta)
    
    # 2. Enviamos
    datos_respuesta = enviar_peticion(url, body)
    
    # 3. Extraemos el resultado final
    texto_final = extraer_texto(datos_respuesta)
    
    return texto_final


# Ejecución del programa
if __name__ == "__main__":
    resultado = test_api_connection("Hola, probando la conexión con mi archivo .env")
    print(resultado)