import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

response = requests.get(url)
if response.status_code == 200:
    models = response.json().get("models", [])
    for model in models:
        print(model.get("name"))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
