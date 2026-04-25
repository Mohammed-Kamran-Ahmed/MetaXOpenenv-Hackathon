import torch
import torch.nn as nn
import torch.optim as optim
import json
import numpy as np

# 1. Define Model Architecture
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


def train():
    # 2. Load Data
    try:
        with open("data/dataset.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Dataset not found. Run generate_dataset.py first.")
        return

    X = []
    y = []
    for item in data:
        m = item["metrics"]
        # Convert dict to flat list of features
        # Order: network_io, disk_alert, error_flag, suspicious, cpu_load
        features = [
            m.get("network_io", 0.0),
            m.get("disk_alert", 0.0),
            m.get("error_flag", 0.0),
            m.get("suspicious", 0.0),
            m.get("cpu_load", 0.0)
        ]
        X.append(features)
        y.append(item["label"])

    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32).view(-1, 1)

    # 3. Initialize Model
    input_size = X.shape[1]
    model = WardenNet(input_size)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)


    # 4. Training Loop
    print("Training Warden Model...")
    history = []
    for epoch in range(1000):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        
        history.append({"epoch": epoch+1, "loss": loss.item()})
        
        if (epoch+1) % 100 == 0:
            print(f'Epoch [{epoch+1}/1000], Loss: {loss.item():.4f}')

    # Save History
    with open("data/training_history.json", "w") as f:
        json.dump(history, f)



    # 5. Save Model
    torch.save(model.state_dict(), "data/warden_model.pth")
    print("\nModel trained and saved to data/warden_model.pth")

    # 6. Test on current data (sanity check)
    with torch.no_grad():
        preds = model(X)
        accuracy = ((preds > 0.5).float() == y).float().mean()
        print(f"Sanity Check Accuracy: {accuracy.item() * 100:.2f}%")

if __name__ == "__main__":
    train()
