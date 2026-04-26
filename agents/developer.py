import os
import time
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

def generate_code(task: str, retries: int = 3) -> str:
    """
    LLM-powered Developer Agent that generates code to solve the given task.
    Includes retry logic and model fallback for demo stability.
    """
    dev_prompt = f"""
You are a Python developer.

Task: {task}

Rules:
- Output ONLY valid Python code
- No markdown formatting or code blocks like ```python
- No explanation or extra text
"""
    
    for attempt in range(retries):
        try:
            # Using 2.0-flash-lite for better quota handling and demo stability
            response = completion(
                model="gemini/gemini-2.0-flash-lite",
                api_key=os.getenv("GEMINI_API_KEY"),
                messages=[{"role": "user", "content": dev_prompt}],
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up markdown if present
            if content.startswith("```python"):
                content = content[len("```python"):].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
            
            return content

        except Exception as e:
            print(f"Developer Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # --- MOCK FALLBACK MODE ---
                # If API fails completely, we return plausible code for the demo
                print("API failed after retries. Entering MOCK FALLBACK MODE for demo stability.")
                task_lower = task.lower()
                
                if any(word in task_lower for word in ["hello", "print", "basic", "simple"]):
                    return "print('Hello! This is a safe system check.')"
                
                if any(word in task_lower for word in ["area", "circle", "calculate", "math", "fibonacci"]):
                    return "import math\nr = 5\nprint(f'Area: {math.pi * r**2}')"
                
                if any(word in task_lower for word in ["loop", "spike", "malicious", "cpu", "stress", "attack"]):
                    return "import time\nprint('Starting high-intensity loop...')\nwhile True:\n    x = 10**10 * 10**10\n    time.sleep(0.0001)" # Simulation of high CPU
                
                if any(word in task_lower for word in ["network", "ping", "upload", "download", "ddos", "flood"]):
                    return "import os\nprint('Simulating network activity...')\nfor i in range(100):\n    os.system('ping -n 1 127.0.0.1')" # Simulation of network I/O
                
                return "print('Task received. System performing routine operations.')"

    return "print('Error: Unknown failure')"
