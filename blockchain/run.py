"""
Blockchain Authentication service — exposes Hyperledger Fabric-style REST API.
Pre-registers all known mesh nodes on startup.
Publishes every new block to MQTT so the dashboard can show the audit log.
"""
import os
import json
import time
import threading
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.ledger import Ledger

app    = Flask(__name__)
CORS(app)
ledger = Ledger()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    mq.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    mq.loop_start()
except Exception as e:
    print(f"[BC] MQTT not available: {e}")

KNOWN_NODES = [
    ("N1","ground"),("N2","ground"),("N3","ground"),("N4","ground"),
    ("N5","ground"),("N6","ground"),("N7","ground"),("N8","ground"),
    ("D1","drone"),("D2","drone"),("SDN","sdn"),
]


def _bootstrap():
    import hashlib, os as _os
    for node_id, node_type in KNOWN_NODES:
        pk = hashlib.sha256(_os.urandom(32)).hexdigest()
        ledger.register_node(node_id, pk, node_type)
        time.sleep(0.1)
    print("[BC] all nodes registered")


threading.Thread(target=_bootstrap, daemon=True).start()


def _publish_events():
    last_count = 0
    while True:
        time.sleep(5)
        chain = ledger.get_chain(limit=20)
        if len(chain) > last_count:
            new_blocks = chain[last_count:]
            for block in new_blocks:
                for tx in block.get("transactions", []):
                    try:
                        mq.publish("qdn/blockchain/event", json.dumps({
                            "node":   tx["node_id"],
                            "event":  tx["action"],
                            "tx_id":  tx["tx_id"],
                            "ts":     tx["ts"],
                        }))
                    except Exception:
                        pass
            last_count = len(chain)


threading.Thread(target=_publish_events, daemon=True).start()


# --- REST ---

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "blockchain", "valid": ledger.is_valid()})


@app.get("/chain")
def chain():
    limit = int(request.args.get("limit", 10))
    return jsonify(ledger.get_chain(limit=limit))


@app.get("/summary")
def summary():
    return jsonify(ledger.chain_summary())


@app.post("/register")
def register():
    data = request.json or {}
    return jsonify(ledger.register_node(data["node_id"], data.get("public_key", ""), data.get("node_type", "ground")))


@app.post("/authenticate")
def authenticate():
    data = request.json or {}
    return jsonify(ledger.authenticate_node(data["node_id"]))


@app.post("/revoke")
def revoke():
    data = request.json or {}
    return jsonify(ledger.revoke_node(data["node_id"]))


@app.get("/identity/<node_id>")
def identity(node_id):
    result = ledger.get_identity(node_id)
    if result:
        return jsonify(result)
    return jsonify({"error": "not found"}), 404


@app.get("/validate")
def validate():
    return jsonify({"valid": ledger.is_valid()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
