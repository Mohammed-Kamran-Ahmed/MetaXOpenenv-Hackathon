import json
import random
import os

def generate_synthetic_dataset(num_samples=100):
    dataset = []
    
    for _ in range(num_samples // 2):
        # SAFE SAMPLES
        dataset.append({
            "task": "Safe Task",
            "metrics": {
                "network_io": random.uniform(0, 100),
                "disk_alert": 0.0,
                "error_flag": 0.0,
                "suspicious": 0.0,
                "cpu_load": random.uniform(0, 15)
            },
            "label": 0
        })
        
        # MALICIOUS SAMPLES
        mal_type = random.choice(["cpu", "network", "disk", "suspicious"])
        if mal_type == "cpu":
            metrics = {
                "network_io": random.uniform(0, 100),
                "disk_alert": 0.0,
                "error_flag": 0.0,
                "suspicious": 0.0,
                "cpu_load": random.uniform(70, 100)
            }
        elif mal_type == "network":
            metrics = {
                "network_io": random.uniform(2000, 10000),
                "disk_alert": 0.0,
                "error_flag": 0.0,
                "suspicious": 0.0,
                "cpu_load": random.uniform(5, 30)
            }
        elif mal_type == "disk":
            metrics = {
                "network_io": random.uniform(0, 100),
                "disk_alert": 1.0,
                "error_flag": 0.0,
                "suspicious": 0.0,
                "cpu_load": random.uniform(10, 50)
            }
        else: # suspicious
            metrics = {
                "network_io": random.uniform(0, 500),
                "disk_alert": 0.0,
                "error_flag": 1.0,
                "suspicious": 1.0,
                "cpu_load": random.uniform(5, 20)
            }
            
        dataset.append({
            "task": "Malicious Task",
            "metrics": metrics,
            "label": 1
        })

    os.makedirs("data", exist_ok=True)
    with open("data/dataset.json", "w") as f:
        json.dump(dataset, f, indent=4)
    print(f"Generated {len(dataset)} high-quality synthetic samples in data/dataset.json")

if __name__ == "__main__":
    generate_synthetic_dataset(200)
