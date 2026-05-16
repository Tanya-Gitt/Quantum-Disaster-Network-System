"""
Post-Quantum Cryptography microservice.
Endpoints: keygen, encapsulate, decapsulate, sign, verify, benchmark.
"""
import os
import json
import time
import threading
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.kyber_kem     import keygen as kyber_keygen, encapsulate, decapsulate
from src.dilithium_sig import keygen as dil_keygen, sign, verify

app = Flask(__name__)
CORS(app)

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    mq.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    mq.loop_start()
except Exception as e:
    print(f"[PQC] MQTT not available: {e}")


# --- Kyber (KEM) ---
@app.post("/kyber/keygen")
def kyber_kg():
    return jsonify(kyber_keygen())


@app.post("/kyber/encapsulate")
def kyber_enc():
    data = request.json or {}
    return jsonify(encapsulate(data["pk_b64"]))


@app.post("/kyber/decapsulate")
def kyber_dec():
    data = request.json or {}
    return jsonify(decapsulate(data["sk_b64"], data["ciphertext_b64"]))


# --- Dilithium (signatures) ---
@app.post("/dilithium/keygen")
def dil_kg():
    return jsonify(dil_keygen())


@app.post("/dilithium/sign")
def dil_sign():
    data = request.json or {}
    return jsonify(sign(data["sk_b64"], data["message"]))


@app.post("/dilithium/verify")
def dil_verify():
    data = request.json or {}
    return jsonify(verify(data["pk_b64"], data["message"], data["signature_b64"]))


# --- Benchmark ---
@app.get("/benchmark")
def benchmark():
    results = {}

    t0 = time.perf_counter()
    kg = kyber_keygen()
    results["kyber_keygen_ms"] = kg["latency_ms"]

    enc = encapsulate(kg.get("pk_b64", ""))
    results["kyber_encap_ms"] = enc["latency_ms"]

    if "pk_b64" in kg:
        dec = decapsulate(kg["sk_b64"], enc["ciphertext_b64"])
        results["kyber_decap_ms"] = dec["latency_ms"]

    dkg = dil_keygen()
    results["dilithium_keygen_ms"] = dkg["latency_ms"]

    if "sk_b64" in dkg:
        s = sign(dkg["sk_b64"], "test-node-identity")
        results["dilithium_sign_ms"] = s["latency_ms"]
        v = verify(dkg["pk_b64"], "test-node-identity", s["signature_b64"])
        results["dilithium_verify_ms"] = v["latency_ms"]

    results["total_ms"] = round((time.perf_counter() - t0) * 1000, 2)

    try:
        mq.publish("qdn/pqc/status", json.dumps({"benchmark": results, "ts": time.time()}))
    except Exception:
        pass

    return jsonify(results)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "pqc"})


# Run benchmark on startup and publish to MQTT
def _startup_bench():
    time.sleep(5)
    try:
        import requests as req
        req.get("http://localhost:5002/benchmark", timeout=30)
    except Exception:
        pass

threading.Thread(target=_startup_bench, daemon=True).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
