# 🛡️ Building the Intelligent Blind Warden: A Behavioral Approach to AI Safety

In the rapidly evolving landscape of autonomous AI agents, a critical question remains: **How do we ensure that an untrusted LLM doesn't execute malicious code behind our backs?**

The traditional approach involves "code scanning" or "prompt filtering"—both of which are prone to obfuscation and prompt injection. For the **Meta Hackathon**, we decided to flip the script. Instead of looking at *what* the agent says, we look at *how* the system reacts.

Meet the **Intelligent Blind Warden**.

---

## 🚀 The Vision: Zero-Trust AI Safety

The core concept of the "Blind Warden" is simple yet powerful: **Safety through observation of behavior, not content.**

Imagine a high-security facility where you can't see what's happening inside a room, but you can see the power consumption, the network traffic, and the temperature. If the room starts drawing 10x more power or making unauthorized outside calls, you shut it down.

That is exactly what our Warden does. It monitors system telemetry—CPU load, Network I/O, Disk activity—to detect malicious patterns like:
- Data exfiltration (Network spikes)
- Cryptojacking (CPU surges)
- Ransomware (Disk spikes)

---

## 🛠️ The Architecture: A Three-Agent Loop

We built this environment using the **OpenEnv** framework, creating a robust, standardized loop:

1.  **👨‍💻 The Untrusted Developer**: A Gemini-powered agent that receives tasks from the user. It can write any Python code, including potentially harmful scripts.
2.  **🚚 The Deployer**: A programmatic bridge that injects this code into a secure **OpenEnv Sandbox**. It captures the "heartbeat" of the system during execution.
3.  **🛡️ The Blind Warden**: A local **PyTorch Neural Network** that receives the raw metrics. It doesn't see the code; it only sees the behavioral "spikes."

### Why this works:
Because the Warden doesn't read the code, it is **immune to prompt injection**. You can't "gaslight" a CPU load spike. You can't "obfuscate" a massive network upload.

---

## 🧠 Technical Deep Dive: The PyTorch Warden

The heart of the project is a 4-layer Multi-Layer Perceptron (MLP) built with PyTorch. 

- **Input Features**: Network I/O, Disk Alerts, Error Flags, Suspicious Process IDs, and CPU Load.
- **Inference**: The model runs locally, ensuring zero-latency safety decisions and total privacy. No external LLM calls are needed to decide if a process is safe.
- **Training**: We used a synthetic data generator to simulate thousands of "Safe" vs. "Malicious" runs, training the Warden to recognize the subtle behavioral signatures of cyber threats.

---

## 📈 Results & Impact

Our simulations showed that the Warden could detect high-confidence threats within milliseconds of execution, often before any significant damage occurred. By providing a **Reinforcement Learning (RL)** signal back to the system, we can further fine-tune the Warden's sensitivity.

### Key Takeaways:
- **Resilience**: Effective against zero-day exploits that bypass traditional signature-based scanners.
- **Standardization**: By using **OpenEnv**, our environment is ready for wider AI Safety research and benchmarking.
- **Privacy**: Safety monitoring happens on the edge, without sending sensitive telemetry to a central server.

---

## 🔮 Future Roadmap

This is just the beginning. The next steps for the Intelligent Blind Warden include:
1.  **Multi-Modal Telemetry**: Integrating memory usage and system call traces.
2.  **Dynamic Sandboxing**: Automatically increasing isolation levels when the Warden's confidence in a threat rises.
3.  **Adversarial Training**: Training the Developer agent to try and "trick" the Warden, creating a co-evolutionary safety loop.

---

### Watch the Demo!
Check out the system in action on our YouTube video (link in the [README.md](README.md)).

*Developed for the Meta Hackathon 2026 using OpenEnv, PyTorch, and Gemini.*
