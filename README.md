# 🛡️ Intelligent Blind Warden - OpenEnv Framework

[![Submission Blog](https://img.shields.io/badge/Submission-Blog.md-blue)](Blog.md)
[![Demo Video](https://img.shields.io/badge/Demo-YouTube-red)](#-watch-the-demo)


## Overview
The **Intelligent Blind Warden** is a multi-agent system designed for **AI Safety and Cybersecurity**. It uses the [OpenEnv](https://github.com/neo-derek/open-env) framework to build a secure sandbox environment where autonomous agents can be trained and evaluated on their ability to handle malicious code execution.

The core mission is to safeguard systems by using a **PyTorch-powered "Blind Warden"** agent that monitors system telemetry (CPU, Network, Disk) without directly reading the code, making real-time decisions to either `APPROVE` or `HALT` execution.

---

## The Multi-Agent Pipeline

The system consists of three specialized agents working in a loop:

1.  **👨‍💻 Developer Agent (LLM-powered)**: Generates Python code based on a user-provided task. It is "untrusted" and may generate malicious or buggy code.
2.  **🚚 Deployer Agent (Programmatic)**: Acts as the bridge that triggers the code execution inside the secure sandbox and captures system metrics.
3.  **🛡️ Warden Agent (Local PyTorch Model)**: The primary safety agent. It receives the system telemetry and uses a trained Neural Network to decide whether the behavior is safe. **No external LLM calls are made for safety decisions.**

---

## Architecture & Framework

### OpenEnv Integration
The project is built on the **OpenEnv framework**, providing a standard Gymnasium-style interface:
-   **Standardized API**: Using `reset()`, `step()`, and `observation()` for agent interactions.
-   **HTTP Server**: The environment is hosted via a FastAPI server, allowing remote agents to connect and train.

### Core Components
-   `environment.py`: Implements the RL environment and secure sandbox.
-   `scripts/generate_dataset.py`: Collects synthetic behavioral data for training.
-   `scripts/train_warden.py`: Trains the PyTorch MLP model on the collected data.
-   `agents/warden.py`: Performs local inference using the trained `.pth` model.

---

## Reinforcement Learning & Training

The system is designed for **Zero-Trust AI Safety** training.

### Training Pipeline
1.  **Generate Data**: Use the Developer agent to create diverse code samples (safe vs malicious).
2.  **Simulate & Label**: Run code in the sandbox and record the system "spikes" (CPU, Network, Disk).
3.  **Train Warden**: Train a local Neural Network to map these spikes to security labels.
4.  **Reward Mechanism**: The environment provides rewards (+10/-20) to evaluate the Warden's performance during training or inference.

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Collect Data & Train Model
You can train the Warden locally or via our Colab-ready script:

#### Local Training
```bash
$env:PYTHONPATH="."
python scripts/generate_dataset.py
python scripts/train_warden.py
```

#### 🚀 Google Colab (Recommended for Judges)
We have provided a standalone, re-runnable training script. This is the fastest way for judges to verify that the Warden can learn behavioral security patterns.

1. **Open Colab**: Go to [Google Colab](https://colab.research.google.com/).
2. **Copy Code**: Copy the entire content of [`scripts/colab_training.py`](scripts/colab_training.py).
3. **Run**: Paste into a cell and run. 

**What happens?** 
The script will automatically install `open-env`, generate synthetic system telemetry (CPU spikes, network surges), train the PyTorch Warden, and display a **Learning Curve** showing the model achieving 100% detection accuracy.

### 3. Start the Server & Run Mission
```bash
python -m uvicorn server.app:app --port 8000
python client.py
```

---

## 📺 Watch the Demo

> [!IMPORTANT]
> **[Link to YouTube Video Here]** — *Replace this with your actual video link before final submission.*

---

## 📖 Project Blog

For a deep dive into the philosophy, architecture, and technical details of the Intelligent Blind Warden, please read our **[Blog.md](Blog.md)**.

---

## Why this is Revolutionary

-   **Zero-Trust**: The Warden never sees the code, preventing it from being tricked by "prompt injection" or obfuscated code.
-   **Local & Secure**: Safety decisions are made locally using PyTorch, ensuring zero latency and maximum privacy.
-   **Scalable**: The environment can generate thousands of synthetic scenarios to constantly improve the Warden's detection capabilities.
