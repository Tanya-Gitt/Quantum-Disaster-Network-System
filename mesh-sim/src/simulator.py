"""
Disaster scenario simulator.
Publishes realistic telemetry for each ground node every 5 seconds.
Can trigger multi-node failure events (earthquake, flood, shutdown).
Simulates drone auto-deployment and AODV rerouting.
"""
import json
import time
import random
import threading
import requests
import numpy as np

GROUND_NODES  = [f"N{i}" for i in range(1, 9)]
DRONE_NODES   = ["D1", "D2"]
ALL_NODES     = GROUND_NODES + DRONE_NODES + ["SDN"]

DISASTER_TYPES = {
    "earthquake":  {"kill": 3, "desc": "Seismic event — BTS infrastructure destroyed"},
    "flood":       {"kill": 2, "desc": "Flooding — ground nodes submerged"},
    "cyberattack": {"kill": 2, "desc": "Coordinated network intrusion"},
    "shutdown":    {"kill": 4, "desc": "Government-mandated internet shutdown"},
    "cyclone":     {"kill": 3, "desc": "Cyclone — aerial + ground damage"},
}


class MeshSimulator:
    def __init__(self, mqtt_client, api_host: str = "localhost"):
        self.mq       = mqtt_client
        self.api_host = api_host
        self._stop    = threading.Event()
        self._lock    = threading.Lock()
        self.scenario_active = False

    def _pub(self, topic: str, payload: dict):
        try:
            self.mq.publish(topic, json.dumps(payload), qos=0)
        except Exception:
            pass

    def _api(self, method: str, path: str, data: dict = None):
        url = f"http://{self.api_host}:5000/api{path}"
        try:
            if method == "POST":
                return requests.post(url, json=data, timeout=3)
            return requests.get(url, timeout=3)
        except Exception:
            return None

    def start_telemetry_loop(self):
        def _run():
            while not self._stop.is_set():
                for node_id in GROUND_NODES:
                    load  = random.uniform(0.1, 0.8)
                    rssi  = random.uniform(-90, -40)
                    temp  = random.uniform(35, 65)
                    self._pub(f"qdn/node/{node_id}/telemetry", {
                        "node_id": node_id,
                        "load":    round(load, 3),
                        "rssi_dbm": round(rssi, 1),
                        "temp_c":   round(temp, 1),
                        "uptime_s": int(time.time() % 86400),
                        "ts":       time.time(),
                    })
                time.sleep(5)

        threading.Thread(target=_run, daemon=True).start()

    def trigger_disaster(self, disaster_type: str = "earthquake") -> dict:
        spec     = DISASTER_TYPES.get(disaster_type, DISASTER_TYPES["earthquake"])
        n_kill   = spec["kill"]
        targets  = random.sample(GROUND_NODES, min(n_kill, len(GROUND_NODES)))
        t_start  = time.time()

        self._pub("qdn/sos", {
            "message": f"DISASTER: {disaster_type.upper()} — {spec['desc']}",
            "targets": targets,
            "ts":      t_start,
        })

        # Kill nodes via API
        for node_id in targets:
            self._api("POST", f"/node/{node_id}/kill")
            self._pub(f"qdn/node/{node_id}/status", {
                "node_id": node_id,
                "status":  "offline",
                "reason":  disaster_type,
                "ts":      time.time(),
            })
            time.sleep(0.3)

        # Wait simulated 4 seconds, then deploy drones
        def _auto_recover():
            time.sleep(4)
            for i, drone in enumerate(DRONE_NODES):
                nearby = targets[i % len(targets)]
                self._api("POST", "/drone/deploy", {
                    "drone_id":   drone,
                    "lat":        28.610 + random.uniform(-0.005, 0.005),
                    "lon":        77.218 + random.uniform(-0.005, 0.005),
                    "connect_to": [targets[(i + 1) % len(targets)]] if targets else [],
                })
                self._pub(f"qdn/node/{drone}/status", {
                    "node_id": drone,
                    "status":  "active",
                    "mission": f"relay for {nearby}",
                    "ts":      time.time(),
                })
                time.sleep(1)

            # Recovery after 90s
            time.sleep(86)
            for node_id in targets:
                self._api("POST", f"/node/{node_id}/restore")
                self._pub(f"qdn/node/{node_id}/status", {
                    "node_id": node_id,
                    "status":  "online",
                    "ts":      time.time(),
                })

        threading.Thread(target=_auto_recover, daemon=True).start()

        return {
            "disaster":     disaster_type,
            "description":  spec["desc"],
            "nodes_killed": targets,
            "drones_queued": DRONE_NODES,
            "recovery_eta_s": 90,
        }

    def stop(self):
        self._stop.set()
