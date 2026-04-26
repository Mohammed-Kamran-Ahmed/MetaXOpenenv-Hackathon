import subprocess
import time
import os
import streamlit as st
import threading
import pandas as pd
import plotly.graph_objects as go
from agents.developer import generate_code
from agents.warden import evaluate_metrics, load_model, WardenNet
from openenv.core import GenericEnvClient, SyncEnvClient
from server.schema import Action
from dotenv import load_dotenv

# 1. Background Server Management
def run_server():
    if not os.path.exists("server_started.txt"):
        print("Starting OpenEnv Server on port 8000...")
        with open("server_started.txt", "w") as f: f.write("1")
        subprocess.run(["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"])

# Start server in a thread if not already running
if not hasattr(st, 'server_started'):
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    st.server_started = True
    time.sleep(5) # Wait for server to boot

# 2. Streamlit UI Logic (Consolidated from dashboard.py)
st.set_page_config(page_title="Intelligent Blind Warden Dashboard", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .agent-log { font-family: 'Courier New', Courier, monospace; background-color: #111827; padding: 10px; border-radius: 5px; border-left: 5px solid #3b82f6; margin-bottom: 10px; }
    .warden-halt { background-color: #991b1b; color: white; padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 24px; }
    .warden-approve { background-color: #065f46; color: white; padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

if 'logs' not in st.session_state: st.session_state.logs = []
if 'metric_history' not in st.session_state: st.session_state.metric_history = pd.DataFrame(columns=["Time", "CPU", "Network"])
if 'total_reward' not in st.session_state: st.session_state.total_reward = 0.0

st.title("🛡️ Intelligent Blind Warden - Simulation")
st.markdown("### Behavioral AI Safety Pipeline powered by OpenEnv & PyTorch")

# UI Layout
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("System Status", "Live Monitoring", delta="Active")
with col2: st.metric("Current Reward", f"{st.session_state.total_reward}", delta="RL Signal")
with col3: st.metric("Warden Engine", "PyTorch MLP", delta="Local Inference")
with col4: st.metric("Sandbox", "OpenEnv Container", delta="Isolated")

st.divider()

st.sidebar.header("Mission Control")
task_input = st.sidebar.text_input("Enter a task for Developer Agent:", "Monitor my system")
start_btn = st.sidebar.button("🚀 Trigger Execution Pipeline")

left_col, right_col = st.columns([2, 1])
with left_col:
    st.subheader("📊 Real-time Telemetry")
    chart_placeholder = st.empty()
    st.subheader("📜 Agent Interaction Pipeline")
    log_placeholder = st.empty()

with right_col:
    st.subheader("🛡️ Warden Decision")
    decision_placeholder = st.empty()
    st.subheader("🧠 Model Confidence")
    confidence_placeholder = st.empty()

def update_ui():
    with log_placeholder.container():
        for agent, msg in reversed(st.session_state.logs[-10:]):
            st.markdown(f'<div class="agent-log"><b>{agent}:</b> {msg}</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.metric_history["Time"], y=st.session_state.metric_history["CPU"], name="CPU Load (%)", line=dict(color='#ef4444')))
    fig.add_trace(go.Scatter(x=st.session_state.metric_history["Time"], y=st.session_state.metric_history["Network"], name="Network I/O (KB)", line=dict(color='#3b82f6')))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
    chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")

if start_btn:
    URL = "http://127.0.0.1:8000"
    client = SyncEnvClient(GenericEnvClient(URL))
    
    st.session_state.logs.append(("👨‍💻 Developer", f"Generating code..."))
    update_ui()
    code = generate_code(task_input)
    
    st.session_state.logs.append(("🚚 Deployer", "Executing in Sandbox..."))
    update_ui()
    client.reset()
    res = client.step(Action(agent_id="DEPLOYER", content="Execute"))
    
    metrics = res.observation.get("system_metrics", {})
    st.session_state.total_reward += res.reward
    
    new_data = pd.DataFrame({"Time": [time.strftime("%H:%M:%S")], "CPU": [metrics.get("cpu_load", 0)], "Network": [metrics.get("network_io", 0)/1024]})
    st.session_state.metric_history = pd.concat([st.session_state.metric_history, new_data], ignore_index=True)
    update_ui()

    st.session_state.logs.append(("🛡️ Warden", "Analyzing Behavior..."))
    update_ui()
    
    import torch
    load_model()
    from agents.warden import _model
    with torch.no_grad():
        feats = [metrics.get("network_io", 0), metrics.get("disk_alert", 0), metrics.get("error_flag", 0), metrics.get("suspicious", 0), metrics.get("cpu_load", 0)]
        pred = _model(torch.tensor([feats], dtype=torch.float32)).item()
    
    decision = "HALT" if pred > 0.5 else "APPROVE"
    if decision == "HALT": decision_placeholder.markdown('<div class="warden-halt">🚨 SECURITY HALT 🚨</div>', unsafe_allow_html=True)
    else: decision_placeholder.markdown('<div class="warden-approve">✅ EXECUTION APPROVED ✅</div>', unsafe_allow_html=True)
    
    confidence_placeholder.progress(pred, text=f"Confidence: {pred:.2%}")
    st.session_state.logs.append(("🛡️ Warden", f"Verdict: {decision}"))
    update_ui()
