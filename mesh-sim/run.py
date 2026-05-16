"""
Mesh simulation service.
Runs continuous node telemetry and exposes disaster trigger endpoints.
"""
import os
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from flask_cors import CORS
from src.simulator import MeshSimulator, DISASTER_TYPES

app = Flask(__name__)
CORS(app)

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
API_HOST  = os.getenv("API_HOST", "localhost")

mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    mq.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    mq.loop_start()
except Exception as e:
    print(f"[SIM] MQTT not available: {e}")

sim = MeshSimulator(mq, api_host=API_HOST)
sim.start_telemetry_loop()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "mesh-sim"})


@app.get("/disasters")
def list_disasters():
    return jsonify(list(DISASTER_TYPES.keys()))


@app.post("/disaster/<disaster_type>")
def trigger(disaster_type):
    if disaster_type not in DISASTER_TYPES:
        return jsonify({"error": "unknown disaster type"}), 400
    result = sim.trigger_disaster(disaster_type)
    return jsonify(result)


@app.post("/disaster/random")
def trigger_random():
    import random
    d = random.choice(list(DISASTER_TYPES.keys()))
    return jsonify(sim.trigger_disaster(d))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
