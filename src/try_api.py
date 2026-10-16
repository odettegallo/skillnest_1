import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api_connection(question):
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-3.5-flash-lite"
    url = f"https://api.openai.com/v1/models/{model}/generate"
    body = {
        "contents": [
            {
                "type": "text",
                "text": question
            }
        ]
    }
    answer = requests.post(url, json=body, headers={"Authorization": f"Bearer {api_key}"})
    return answer.json()["results"][0]["content"][0]["text"]
    print(test_api_connection("Hola, probando la conexión con mi archivo .env"))