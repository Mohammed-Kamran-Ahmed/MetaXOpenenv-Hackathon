import os
from litellm import completion

def generate_code(task: str) -> str:
    """
    LLM-powered Developer Agent that generates code to solve the given task.
    """
    dev_prompt = f"""
You are a Python developer.

Task: {task}

Rules:
- Output ONLY valid Python code
- No markdown formatting or code blocks like ```python
- No explanation or extra text
"""
    try:
        response = completion(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            messages=[{"role": "user", "content": dev_prompt}],
            temperature=0.2
        )
        # Clean up in case markdown was included
        content = response.choices[0].message.content.strip()
        if content.startswith("```python"):
            content = content[len("```python"):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()
        return content

    except Exception as e:
        print(f"Developer LLM Call Failed: {e}")
        return "print('Error generating code')"
