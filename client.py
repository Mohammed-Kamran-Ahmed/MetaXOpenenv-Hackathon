import os
import requests
from openenv.core import SyncEnvClient, GenericEnvClient
from server.schema import Action

from agents.developer import generate_code
from agents.deployer import collect_metrics
from agents.warden import evaluate_metrics

# Make sure GEMINI_API_KEY is set in your environment
os.environ["GEMINI_API_KEY"] = "AIzaSyBZTdcmdKNSnHXhWnQxJuCYFF_aYXchUIs"

URL = "http://127.0.0.1:8000"

def run_mission():
    print("Starting Intelligent Blind Warden (OpenEnv Powered)...")

    # Connect to the OpenEnv standard HTTP server
    try:
        async_client = GenericEnvClient(URL)
        client = SyncEnvClient(async_client)
        result = client.reset()
        obs = result.observation
    except Exception as e:
        print(f"Start FastAPI server first! Error: {e}")
        return

    # Task
    task = "Write a short Python script to ping google.com and print success."

    # 1. DEVELOPER AGENT (LLM)
    print("\n[Developer] Generating code...")
    generated_code = generate_code(task)
    print("Developer generated code:\n", generated_code)

    # Step the environment with Developer action
    action = Action(agent_id="DEVELOPER", content=generated_code)
    result = client.step(action)
    obs = result.observation

    # 2. DEPLOYER AGENT
    print("\n[Deployer] Triggering execution and collecting metrics...")
    deployer_cmd = collect_metrics()
    
    # Step the environment with Deployer action
    action = Action(agent_id="DEPLOYER", content=deployer_cmd)
    result = client.step(action)
    obs = result.observation

    # Extract metrics from the observation
    metrics = obs.get("system_metrics", {})
    logs = obs.get("logs", {})
    print("Metrics:", metrics)


    # 3. WARDEN AGENT (LLM)
    print("\n[Warden] Evaluating metrics...")
    decision = evaluate_metrics(task, metrics, logs)
    print(f"Warden Decision: {decision}")

    # Step the environment with Warden action to finalize reward
    action = Action(agent_id="WARDEN", content=decision)
    result = client.step(action)
    
    reward = result.reward
    print(f"\nFinal Reward from Environment: {reward}")

    # 4. DEPLOY IF SAFE (Real-world action outside environment)
    if decision == "APPROVE":
        print("Deploying safely...")
        # Execute natively as deployment simulation
        import subprocess
        subprocess.run(["python", "-c", generated_code])
    else:
        print("Blocked by Warden")


if __name__ == "__main__":
    run_mission()