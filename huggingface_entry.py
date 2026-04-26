import subprocess
import time
import os
import streamlit as st
import threading

# 1. Start OpenEnv Server in a background thread
def run_server():
    print("Starting OpenEnv Server on port 8000...")
    subprocess.run(["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"])

if not os.environ.get("SERVER_STARTED"):
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    os.environ["SERVER_STARTED"] = "1"
    time.sleep(5) # Give it time to warm up

# 2. Redirect to our existing Dashboard logic
# We can just import and run the dashboard logic here or use st._rerun()
# For HF, we will copy the dashboard logic into this file for a single-file entry point
from dashboard import run_simulation, update_ui, task_input, start_btn

# The rest of the app.py will be our dashboard.py logic...
# (I'll keep it simple: HF will run this file as a streamlit app)
