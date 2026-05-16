"""
AI Engine service — exposes REST endpoints and publishes routing decisions via MQTT.
"""
import os
import json
import threading
import time
import numpy as np
import requests
from flask import Flask, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt

from src.lstm_predictor import LSTMPredictor
from src.ppo_agent       import PPOAgent
from src.mesh_env        import N_NODES, N_EDGES

app = Flask(__name__)
CORS(app)

API_HOST  = os.getenv("API_HOST", "localhost")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

lstm  = LSTMPredictor(n_nodes=N_NODES)
agent = PPOAgent()

# --- MQTT ---
mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    mq.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    mq.loop_start()
except Exception as e:
    print(f"[AI] MQTT not available: {e}")


def publish(topic: str, payload: dict):
    try:
        mq.publish(topic, json.dumps(payload), qos=0)
    except Exception:
        pass


# --- Background loop: fetch topology → predict → decide → publish ---
def ai_loop():
    edge_active = np.ones(N_EDGES, dtype=np.float32)
    while True:
        time.sleep(3)
        try:
            r = requests.get(f"http://{API_HOST}:5000/api/topology", timeout=2)
            topo = r.json()
            nodes = topo.get("nodes", [])
            if not nodes:
                continue

            load_vec = np.array([n["load"] for n in nodes[:N_NODES]], dtype=np.float32)
            # Pad if fewer nodes returned than expected
            if len(load_vec) < N_NODES:
                load_vec = np.pad(load_vec, (0, N_NODES - len(load_vec)))

            offline = np.array([1.0 if n["status"] != "offline" else 0.0 for n in nodes[:N_NODES]], dtype=np.float32)
            # Edge active: approximate from node offline mask
            for i, (u, v) in enumerate([(0,1),(0,4),(0,10),(1,2),(1,6),(2,5),(2,3),(3,7),(3,10),(4,6),(5,7),(6,10)]):
                edge_active[i] = float(offline[u] and offline[v])

            lstm.update(load_vec)
            predicted = lstm.predict()
            rmse      = lstm.rmse(load_vec)

            decision = agent.decide(load_vec, edge_active)

            payload = {
                "timestamp":    time.time(),
                "loads":        load_vec.tolist(),
                "predicted":    predicted.tolist(),
                "rmse":         round(rmse, 4),
                "routing":      decision,
            }
            publish("qdn/ai/routing", payload)

        except Exception as e:
            print(f"[AI] loop error: {e}")


threading.Thread(target=ai_loop, daemon=True).start()


# --- REST ---
@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "ai-engine"})


@app.get("/predict")
def predict():
    pred = lstm.predict()
    return jsonify({"predicted_loads": pred.tolist()})


@app.post("/retrain")
def retrain():
    agent.retrain()
    return jsonify({"status": "retraining started"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
