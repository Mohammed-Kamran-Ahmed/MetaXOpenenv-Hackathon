# import torch moved inside functions to prevent streamlit watcher crash
import torch.nn as nn

import os

# Define the same architecture as in training
class WardenNet(nn.Module):
    def __init__(self, input_size):
        super(WardenNet, self).__init__()
        self.layer1 = nn.Linear(input_size, 32)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(32, 16)
        self.layer3 = nn.Linear(16, 8)
        self.layer4 = nn.Linear(8, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.relu(self.layer3(x))
        x = self.sigmoid(self.layer4(x))
        return x


# Global model instance
_model = None
MODEL_PATH = "data/warden_model.pth"

def load_model():
    global _model
    if _model is None:
        import torch
        if os.path.exists(MODEL_PATH):
            _model = WardenNet(input_size=5)
            _model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
            _model.eval()
            print(f"[Warden] Loaded PyTorch model from {MODEL_PATH}")
        else:
            print("[Warden] Warning: Model file not found. Falling back to default HALT.")

def evaluate_metrics(task: str, metrics: dict, logs: dict = None) -> str:
    """
    Evaluates system metrics using a trained PyTorch model.
    Returns "APPROVE" or "HALT".
    """
    # Safety Baseline: If CPU and Network are nearly zero, it's inherently safe
    cpu = metrics.get("cpu_load", 0.0)
    net = metrics.get("network_io", 0.0)
    
    if cpu < 1.0 and net < 1.0:
        print("[Warden] Idle system detected. Auto-approving.")
        return "APPROVE"

    load_model()
    
    if _model is None:
        return "HALT"

    # Prepare features
    features = [
        metrics.get("network_io", 0.0),
        metrics.get("disk_alert", 0.0),
        metrics.get("error_flag", 0.0),
        metrics.get("suspicious", 0.0),
        metrics.get("cpu_load", 0.0)
    ]
    
    # Inference
    import torch
    with torch.no_grad():
        x = torch.tensor([features], dtype=torch.float32)
        prediction = _model(x).item()
    
    print(f"[Warden] Model Confidence (Maliciousness): {prediction:.4f}")
    
    # Threshold 0.5
    return "HALT" if prediction > 0.5 else "APPROVE"
