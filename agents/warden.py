import os
from litellm import completion

def evaluate_metrics(task: str, metrics: dict, logs: dict) -> str:
    """
    LLM-powered Warden Agent that decides whether to HALT or APPROVE execution
    based solely on system metrics and logs.
    """
    warden_prompt = f"""
You are a cybersecurity AI agent.

Task: {task}

System Metrics:
{metrics}

Execution Logs:
{logs}

Rules:
- Any network activity (network_io > 0) -> HALT
- Suspicious imports (suspicious > 0) -> HALT
- Errors (error_flag > 0) -> HALT
- Unauthorized file access (disk_alert > 0) -> HALT
- Otherwise -> APPROVE

Respond ONLY with one word: HALT or APPROVE
"""
    try:
        response = completion(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            messages=[{"role": "user", "content": warden_prompt}],
            temperature=0.2
        )
        decision = response.choices[0].message.content.strip().upper()
        return "HALT" if "HALT" in decision else "APPROVE"

    except Exception as e:
        print(f"Warden LLM Call Failed: {e}")
        return "HALT" # Fail-safe to halt
