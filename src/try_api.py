import os
import requests
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

def test_api_connection(question):
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-3.5-flash-lite"  # O "gemini-3.5-flash-lite" según te exijan
    
    # La API de Gemini espera la key como parámetro en la URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Estructura JSON correcta que exige Google Generative Language API
    body = {
        "contents": [
            {
                "parts": [
                    {"text": question}
                ]
            }
        ]
    }
    
    # Hacemos la petición POST (sin cabecera Bearer, la key va en la URL)
    answer = requests.post(url, json=body)
    
    # Parseamos la respuesta JSON
    data = answer.json()
    
    # Manejo de errores por si la API rechaza la petición
    if "candidates" not in data:
        return f"Error en la respuesta de la API: {data}"
        
    # Extracción correcta del texto dentro de la respuesta de Google
    return data["candidates"][0]["content"]["parts"][0]["text"]

# ESTO ES LO QUE FALTABA: Llamar a la función fuera de su definición para que se ejecute e imprima
if __name__ == "__main__":
    resultado = test_api_connection("Hola, probando la conexión con mi archivo .env")
    print(resultado)