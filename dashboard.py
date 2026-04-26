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

load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="🛡️ Intelligent Blind Warden HUD",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM GOATED CSS ---
st.markdown("""
    <style>
    /* Main Dark Theme */
    .stApp { background-color: #05070a; color: #e0e6ed; }
    
    /* Hero Section */
    .hero-container {
        padding: 2rem;
        background: linear-gradient(90deg, rgba(5,7,10,1) 0%, rgba(20,30,48,1) 100%);
        border-bottom: 2px solid #1e293b;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    /* Pipeline Steps */
    .pipeline-step {
        padding: 10px;
        border-radius: 8px;
        background: #111827;
        border-left: 4px solid #374151;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .pipeline-active {
        border-left-color: #3b82f6;
        background: #1e3a8a33;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
    }
    .pipeline-success { border-left-color: #10b981; }
    .pipeline-alert { border-left-color: #ef4444; }

    /* HUD Metrics */
    .hud-card {
        background: #0f172a;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        text-align: center;
    }
    
    /* Warden Alert HUD */
    .warden-box {
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        animation: pulse 2s infinite;
    }
    .halt-mode { background: rgba(153, 27, 27, 0.2); border: 2px solid #ef4444; color: #f87171; }
    .approve-mode { background: rgba(6, 95, 70, 0.2); border: 2px solid #10b981; color: #34d399; }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #05070a; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logs' not in st.session_state: st.session_state.logs = []
if 'metric_history' not in st.session_state: st.session_state.metric_history = pd.DataFrame(columns=["Time", "CPU", "Network"])
if 'total_reward' not in st.session_state: st.session_state.total_reward = 0.0
if 'pipeline_stage' not in st.session_state: st.session_state.pipeline_stage = 0

# --- SIDEBAR: MISSION CONTROL ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield-configuration.png", width=80)
    st.title("Warden Mission Control")
    st.markdown("---")
    
    task_input = st.text_area("🎯 Enter Developer Objective:", "Calculate the area of a circle", height=100)
    st.info("The Developer Agent will attempt to generate code for this task inside the sandbox.")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        start_btn = st.button("🚀 DEPLOY", use_container_width=True)
    with col_btn2:
        clear_btn = st.button("🗑️ RESET", use_container_width=True)

    if clear_btn:
        st.session_state.logs = []
        st.session_state.metric_history = pd.DataFrame(columns=["Time", "CPU", "Network"])
        st.session_state.total_reward = 0.0
        st.session_state.pipeline_stage = 0
        st.rerun()

    st.markdown("---")
    st.subheader("🛠️ System Config")
    st.toggle("Advanced Debug Logs", value=False)
    st.caption("v1.2.0 - OpenEnv Stable Build")

# --- MAIN INTERFACE ---

# 1. Hero Section
st.markdown(f"""
    <div class="hero-container">
        <h1>🛡️ Intelligent Blind Warden <span style="color: #3b82f6; font-size: 0.5em; vertical-align: middle;">BETA</span></h1>
        <p style="color: #94a3b8; font-size: 1.1em;">Behavioral AI Safety Pipeline: Monitoring Telemetry, Not Just Code.</p>
    </div>
""", unsafe_allow_html=True)

# 2. Top HUD Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    cpu_val = st.session_state.metric_history["CPU"].iloc[-1] if not st.session_state.metric_history.empty else 0
    st.metric("System Load", f"{cpu_val:.1f}%", delta=f"{cpu_val-20:.1f}%" if cpu_val else "Idle")
with col2:
    net_val = st.session_state.metric_history["Network"].iloc[-1] if not st.session_state.metric_history.empty else 0
    st.metric("Network I/O", f"{net_val:.1f} KB", delta=f"{net_val:.1f}" if net_val else "Quiet")
with col3:
    st.metric("Total Reward", f"{st.session_state.total_reward:.1f}", delta="Safety Score")
with col4:
    st.metric("Model Status", "Inference Active", delta="PyTorch 2.0")

st.markdown("<br>", unsafe_allow_html=True)

# 3. Simulation & Pipeline
left_col, right_col = st.columns([2, 1])

with left_col:
    # Telemetry Chart
    st.subheader("📊 Real-time Behavioral Telemetry")
    chart_placeholder = st.empty()
    
    # Render Initial Chart
    def render_chart():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.metric_history["Time"], y=st.session_state.metric_history["CPU"], name="CPU Load (%)", line=dict(color='#ef4444', width=3), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.1)'))
        fig.add_trace(go.Scatter(x=st.session_state.metric_history["Time"], y=st.session_state.metric_history["Network"], name="Network (KB)", line=dict(color='#3b82f6', width=3)))
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        chart_placeholder.plotly_chart(fig, use_container_width=True)

    render_chart()

    # Agent Timeline
    st.subheader("📜 Agent Interaction Pipeline")
    log_placeholder = st.empty()

with right_col:
    # Warden HUD
    st.subheader("🛡️ Warden HUD")
    decision_placeholder = st.empty()
    confidence_placeholder = st.empty()
    
    # Pipeline Visualizer
    st.subheader("🏗️ Pipeline Status")
    p1 = st.empty()
    p2 = st.empty()
    p3 = st.empty()
    p4 = st.empty()

    def update_pipeline_ui(stage):
        st.session_state.pipeline_stage = stage
        p1.markdown(f'<div class="pipeline-step {"pipeline-active" if stage==1 else "pipeline-success" if stage>1 else ""}"><b>STEP 1:</b> Developer (LLM Code Gen)</div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="pipeline-step {"pipeline-active" if stage==2 else "pipeline-success" if stage>2 else ""}"><b>STEP 2:</b> Deployer (Sandbox Injection)</div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="pipeline-step {"pipeline-active" if stage==3 else "pipeline-success" if stage>3 else ""}"><b>STEP 3:</b> Execution (Telemetry Capture)</div>', unsafe_allow_html=True)
        p4.markdown(f'<div class="pipeline-step {"pipeline-active" if stage==4 else "pipeline-success" if stage>4 else ""}"><b>STEP 4:</b> Warden (Behavioral AI Inference)</div>', unsafe_allow_html=True)

    update_pipeline_ui(st.session_state.pipeline_stage)

    # Neural Insights
    with st.expander("🧠 View Warden Neural Insights"):
        if os.path.exists("data/training_history.json"):
            history_data = pd.read_json("data/training_history.json")
            st.line_chart(history_data.set_index("epoch")["loss"], color="#ef4444")
            st.caption("Current Model: BCE Loss convergence over 1000 iterations.")
        else:
            st.warning("Training history not found. Train the model to see insights.")

# --- SIMULATION LOGIC ---
def run_simulation(task):
    URL = "http://127.0.0.1:8000"
    try:
        async_client = GenericEnvClient(URL)
        client = SyncEnvClient(async_client)
    except Exception as e:
        st.error("OpenEnv Server is offline. Please start it using 'uvicorn server.app:app'")
        return

    # 1. Developer
    update_pipeline_ui(1)
    st.session_state.logs.append(("👨‍💻 Developer", f"Generating code for: '{task}'..."))
    update_logs_ui()
    code = generate_code(task)
    time.sleep(1)

    # 2. Deployer
    update_pipeline_ui(2)
    st.session_state.logs.append(("🚚 Deployer", "Injecting into OpenEnv Sandbox..."))
    update_logs_ui()
    client.reset()
    client.step(Action(agent_id="DEVELOPER", content=code))
    time.sleep(1)

    # 3. Execution
    update_pipeline_ui(3)
    st.session_state.logs.append(("📦 Sandbox", "Capturing behavioral spikes..."))
    update_logs_ui()
    result = client.step(Action(agent_id="DEPLOYER", content="Execute"))
    
    metrics = result.observation.get("system_metrics", {})
    st.session_state.total_reward += result.reward
    
    new_data = pd.DataFrame({
        "Time": [time.strftime("%H:%M:%S")],
        "CPU": [metrics.get("cpu_load", 0)],
        "Network": [metrics.get("network_io", 0) / 1024]
    })
    st.session_state.metric_history = pd.concat([st.session_state.metric_history, new_data], ignore_index=True)
    render_chart()
    time.sleep(1)

    # 4. Warden
    update_pipeline_ui(4)
    st.session_state.logs.append(("🛡️ Warden", "Analyzing telemetry signatures..."))
    update_logs_ui()
    
    from agents.warden import load_model, _model
    import torch
    load_model()
    
    features = [metrics.get("network_io", 0.0), metrics.get("disk_alert", 0.0), metrics.get("error_flag", 0.0), metrics.get("suspicious", 0.0), metrics.get("cpu_load", 0.0)]
    
    with torch.no_grad():
        from agents.warden import _model
        x = torch.tensor([features], dtype=torch.float32)
        prediction = _model(x).item() if _model else 1.0
        decision = "HALT" if prediction > 0.5 else "APPROVE"

    # Final HUD Update
    if decision == "HALT":
        decision_placeholder.markdown('<div class="warden-box halt-mode">🚨 SECURITY HALT 🚨</div>', unsafe_allow_html=True)
    else:
        decision_placeholder.markdown('<div class="warden-box approve-mode">✅ SAFE TO EXECUTE ✅</div>', unsafe_allow_html=True)
    
    confidence_placeholder.progress(prediction, text=f"Maliciousness Confidence: {prediction:.2%}")
    st.session_state.logs.append(("🛡️ Warden", f"Decision finalized: {decision}"))
    update_logs_ui()
    update_pipeline_ui(0) # Reset pipeline for next run

def update_logs_ui():
    with log_placeholder.container():
        for agent, msg in reversed(st.session_state.logs[-10:]):
            st.markdown(f'<div style="background: #111827; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #3b82f6;"><b>{agent}:</b> {msg}</div>', unsafe_allow_html=True)

if start_btn:
    run_simulation(task_input)

