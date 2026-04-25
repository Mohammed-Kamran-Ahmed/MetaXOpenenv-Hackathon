import streamlit as st
import os
import pandas as pd

import time
import random
import plotly.graph_objects as go
from agents.developer import generate_code
from agents.warden import evaluate_metrics, load_model, WardenNet
from openenv.core import GenericEnvClient, SyncEnvClient

from server.schema import Action
from dotenv import load_dotenv
import threading
import queue

load_dotenv()

# Page Config
st.set_page_config(page_title="Intelligent Blind Warden Dashboard", layout="wide", page_icon="🛡️")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .agent-log { font-family: 'Courier New', Courier, monospace; background-color: #111827; padding: 10px; border-radius: 5px; border-left: 5px solid #3b82f6; margin-bottom: 10px; }
    .warden-halt { background-color: #991b1b; color: white; padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 24px; }
    .warden-approve { background-color: #065f46; color: white; padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

# Session State for Logs and Metrics
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'metric_history' not in st.session_state:
    st.session_state.metric_history = pd.DataFrame(columns=["Time", "CPU", "Network"])
if 'total_reward' not in st.session_state:
    st.session_state.total_reward = 0.0

# --- HEADER ---
st.title("🛡️ Intelligent Blind Warden - Simulation")
st.markdown("### Behavioral AI Safety Pipeline powered by OpenEnv & PyTorch")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("System Status", "Live Monitoring", delta="Active")
with col2:
    st.metric("Current Reward", f"{st.session_state.total_reward}", delta="RL Signal")
with col3:
    st.metric("Warden Engine", "PyTorch MLP", delta="Local Inference")
with col4:
    st.metric("Sandbox", "OpenEnv Container", delta="Isolated")

st.divider()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Mission Control")
task_input = st.sidebar.text_input("Enter a task for Developer Agent:", "Write a script to ping google.com")
start_btn = st.sidebar.button("🚀 Trigger Execution Pipeline")
clear_btn = st.sidebar.button("🗑️ Clear Logs")

if clear_btn:
    st.session_state.logs = []
    st.session_state.metric_history = pd.DataFrame(columns=["Time", "CPU", "Network"])
    st.session_state.total_reward = 0.0
    st.rerun()

# --- MAIN LAYOUT ---
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
    
    st.subheader("🏗️ Pipeline Visualizer")

    st.code("""
    [User Task] 
        ↓
    👨‍💻 Developer (LLM) 
        ↓ 
    🚚 Deployer (Bridge) 
        ↓
    📦 OpenEnv Sandbox (Execution)
        ↓
    🛡️ Warden (PyTorch AI)
        ↓
    [Decision: APPROVE / HALT]
    """, language="text")


# --- SIMULATION LOGIC ---
def run_simulation(task):
    URL = "http://127.0.0.1:8000"
    try:
        async_client = GenericEnvClient(URL)
        client = SyncEnvClient(async_client)
    except Exception as e:
        st.error(f"Could not connect to OpenEnv Server. Please run 'uvicorn server.app:app' first.")
        return

    # Phase 1: Developer
    st.session_state.logs.append(("👨‍💻 Developer", f"Generating code for task: '{task}'"))
    update_ui()
    code = generate_code(task)
    st.session_state.logs.append(("👨‍💻 Developer", f"Code generated successfully."))
    update_ui()
    time.sleep(1)

    # Phase 2: Deployer
    st.session_state.logs.append(("🚚 Deployer", "Injecting code into OpenEnv Sandbox..."))
    update_ui()
    client.reset()
    action_dev = Action(agent_id="DEVELOPER", content=code)
    client.step(action_dev)
    
    st.session_state.logs.append(("🚚 Deployer", "Triggering execution and capturing telemetry..."))
    update_ui()
    action_dep = Action(agent_id="DEPLOYER", content="Execute")
    result_dep = client.step(action_dep)
    
    # Phase 3: Metrics & Environment
    obs = result_dep.observation
    metrics = obs.get("system_metrics", {})
    reward = result_dep.reward
    st.session_state.total_reward += reward
    
    # Update Charts
    new_data = pd.DataFrame({
        "Time": [time.strftime("%H:%M:%S")],
        "CPU": [metrics.get("cpu_load", 0)],
        "Network": [metrics.get("network_io", 0) / 1024] # KB
    })
    st.session_state.metric_history = pd.concat([st.session_state.metric_history, new_data], ignore_index=True)
    update_ui()

    # Phase 4: Warden
    st.session_state.logs.append(("🛡️ Warden", "Analyzing behavioral signatures..."))
    update_ui()
    time.sleep(1)
    
    # We call evaluate_metrics but we need the confidence score too (custom logic for UI)
    from agents.warden import load_model, _model, WardenNet
    import torch
    load_model()
    
    features = [
        metrics.get("network_io", 0.0),
        metrics.get("disk_alert", 0.0),
        metrics.get("error_flag", 0.0),
        metrics.get("suspicious", 0.0),
        metrics.get("cpu_load", 0.0)
    ]
    
    with torch.no_grad():
        from agents.warden import _model
        x = torch.tensor([features], dtype=torch.float32)
        prediction = _model(x).item() if _model else 1.0
        decision = "HALT" if prediction > 0.5 else "APPROVE"

    # Final Display
    if decision == "HALT":
        decision_placeholder.markdown('<div class="warden-halt">🚨 SECURITY HALT 🚨</div>', unsafe_allow_html=True)
    else:
        decision_placeholder.markdown('<div class="warden-approve">✅ EXECUTION APPROVED ✅</div>', unsafe_allow_html=True)
    
    confidence_placeholder.progress(prediction, text=f"Maliciousness Confidence: {prediction:.2%}")
    
    st.session_state.logs.append(("🛡️ Warden", f"Decision: {decision} (Reward: {reward})"))
    update_ui()

    # Show training history if available
    if os.path.exists("data/training_history.json"):
        with st.expander("📉 View Model Training Insight"):
            history_data = pd.read_json("data/training_history.json")
            st.line_chart(history_data.set_index("epoch")["loss"])


def update_ui():
    # Update Logs
    with log_placeholder.container():
        for agent, msg in reversed(st.session_state.logs[-10:]):
            st.markdown(f'<div class="agent-log"><b>{agent}:</b> {msg}</div>', unsafe_allow_html=True)
    
    # Update Charts directly using the placeholder
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.metric_history["Time"], y=st.session_state.metric_history["CPU"], name="CPU Load (%)", line=dict(color='#ef4444')))
    fig.add_trace(go.Scatter(x=st.session_state.metric_history["Time"], y=st.session_state.metric_history["Network"], name="Network I/O (KB)", line=dict(color='#3b82f6')))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
    chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")


if start_btn:
    run_simulation(task_input)

