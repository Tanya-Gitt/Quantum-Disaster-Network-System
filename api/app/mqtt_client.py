"""
MQTT bridge — subscribe to mesh topics and relay events to WebSocket clients.
"""
import os
import json
import threading
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

TOPICS = [
    "qdn/node/+/status",
    "qdn/node/+/telemetry",
    "qdn/sos",
    "qdn/ai/routing",
    "qdn/pqc/status",
    "qdn/blockchain/event",
]


def start_mqtt(socketio):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(c, userdata, flags, rc, props=None):
        for topic in TOPICS:
            c.subscribe(topic)

    def on_message(c, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except Exception:
            payload = {"raw": msg.payload.decode()}

        topic = msg.topic
        if "sos" in topic:
            socketio.emit("sos_alert", payload)
        elif "telemetry" in topic:
            socketio.emit("telemetry", payload)
        elif "routing" in topic:
            socketio.emit("ai_routing", payload)
        elif "pqc" in topic:
            socketio.emit("pqc_status", payload)
        elif "blockchain" in topic:
            socketio.emit("blockchain_event", payload)
        else:
            socketio.emit("node_event", {"topic": topic, "payload": payload})

    client.on_connect = on_connect
    client.on_message = on_message

    def _run():
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            client.loop_forever()
        except Exception as e:
            print(f"[MQTT] connection failed: {e}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
