import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

print(f"Testing with Key: {os.getenv('GEMINI_API_KEY')[:10]}...")

try:
    response = completion(
        model="gemini/gemini-pro",
        messages=[{"role": "user", "content": "Say hello"}],
    )
    print("Response Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Response Failed: {e}")
