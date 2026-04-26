import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')

try:
    response = model.generate_content("Say hello")
    print("Native Success!")
    print(response.text)
except Exception as e:
    print(f"Native Failed: {e}")
