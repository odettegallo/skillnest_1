import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_gemini_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("GEMINI_API_KEY is valid and the request was successful.")
    else:
        print(f"Failed to validate GEMINI_API_KEY. Status code: {response.status_code}, Response: {response.text}")