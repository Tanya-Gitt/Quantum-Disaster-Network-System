<div align="center">

# Quantum Disaster Network

**AI-Driven Self-Healing Quantum-Secure Disaster Communication Network**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

*B.Tech Final Year Project — Computer Networks*

</div>

---

## Overview

A fully software-based disaster communication network that combines **post-quantum cryptography**, **AI-driven self-healing**, and **blockchain integrity** to maintain communication during natural disasters, cyberattacks, and infrastructure failures.

When nodes go offline, the network automatically reroutes traffic, deploys drone relays, and restores connectivity — all in real time, visible on a live topology map.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Dashboard                       │
│         Live Map · Metrics · Disaster Controls           │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket
┌────────────────────▼────────────────────────────────────┐
│                    Flask API (port 5000)                  │
│         REST Endpoints · Socket.IO · Topology            │
└──────┬─────────────┬──────────────┬──────────────────────┘
       │             │              │
┌──────▼───┐  ┌──────▼───┐  ┌──────▼───┐
│ AI Engine│  │  PQC     │  │Blockchain│
│ port 5001│  │ port 5002│  │ port 5004│
│          │  │          │  │          │
│ LSTM     │  │ Kyber    │  │ SHA-256  │
│ PPO/RL   │  │ 1024     │  │ Ledger   │
└──────────┘  │Dilithium3│  └──────────┘
              └──────────┘
┌─────────────────────────────────────────────────────────┐
│               Eclipse Mosquitto MQTT (port 1883)         │
│              IoT Telemetry · Node Heartbeats             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 Mesh Simulator (port 5003)                │
│         AODV Routing · Disaster Triggers · Drones        │
└─────────────────────────────────────────────────────────┘
```

---

## Features

- **Self-Healing Network** — Nodes detect failures and reroute automatically via AODV mesh protocol
- **AI Routing** — LSTM predicts traffic load; PPO reinforcement learning selects optimal paths
- **Post-Quantum Crypto** — CRYSTALS-Kyber 1024 key encapsulation + Dilithium 3 signatures
- **Drone Deployment** — UAV relay nodes auto-deploy when ground infrastructure fails
- **Blockchain Ledger** — Every topology change is hash-chained and tamper-evident
- **Live Dashboard** — Real-time map with node status, metrics, SOS alerts, and disaster simulation

---

## Services

| Service | Port | Stack |
|---|---|---|
| Dashboard | 3000 | React 18, Leaflet.js, Socket.IO |
| API | 5000 | Flask, Flask-SocketIO, eventlet |
| AI Engine | 5001 | TensorFlow 2.16, Stable-Baselines3, Gymnasium |
| PQC | 5002 | kyber-py 1.2.0, pycryptodome |
| Mesh Sim | 5003 | Flask, paho-mqtt, NumPy |
| Blockchain | 5004 | Flask, SHA-256 |
| MQTT Broker | 1883/9001 | Eclipse Mosquitto 2.0 |

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- 8 GB RAM minimum (AI engine is large)
- 10 GB free disk space

### Run

```bash
git clone https://github.com/YOUR_USERNAME/quantum-disaster-net.git
cd quantum-disaster-net
docker compose up --build
```

Open **http://localhost:3000** in your browser.

> First build takes 15–20 minutes (downloads TensorFlow + PyTorch). Subsequent starts are instant.

### Stop

```bash
docker compose down
```

---

## Disaster Simulation

Once the dashboard is open, use the **Disaster Controls** panel to simulate:

| Scenario | Effect |
|---|---|
| Earthquake | Kills 3 ground nodes, triggers mesh reroute |
| Flood | Disables low-lying nodes, deploys drone D1 |
| Cyberattack | Simulates node compromise, blockchain flags it |
| Shutdown | Full sector blackout, AI finds alternate path |
| Cyclone | Multiple node failures, both drones deployed |

Watch the topology map update live as nodes go red, drones activate (green), and paths reroute.

---

## API Reference

```
GET  /api/topology          → Full network graph (nodes + edges)
POST /api/node/<id>/kill    → Take a node offline
POST /api/node/<id>/restore → Bring a node back online
POST /api/drone/deploy      → Deploy a UAV relay node
GET  /api/path              → AI-recommended best path

GET  /pqc/keygen            → Generate Kyber-1024 keypair
POST /pqc/encapsulate       → Encapsulate shared secret
GET  /blockchain/chain      → Full blockchain ledger
GET  /ai/predict            → Current AI routing decision
GET  /mesh/status           → Mesh network topology
```

---

## Project Structure

```
quantum-disaster-net/
├── api/                    # Flask REST API + WebSocket
│   └── app/
│       ├── topology.py     # Network graph, node management
│       ├── routes.py       # REST endpoints
│       ├── events.py       # Socket.IO real-time events
│       └── mqtt_client.py  # MQTT subscriber
├── ai-engine/              # ML routing engine
│   └── src/
│       ├── lstm_predictor.py   # Traffic load forecasting
│       ├── mesh_env.py         # Gymnasium RL environment
│       └── ppo_agent.py        # PPO routing agent
├── pqc/                    # Post-quantum cryptography
│   └── src/
│       ├── kyber_kem.py        # Key encapsulation
│       └── dilithium_sig.py    # Digital signatures
├── blockchain/             # Tamper-evident ledger
│   └── src/
│       └── ledger.py           # SHA-256 chained blocks
├── mesh-sim/               # Mesh network simulator
│   └── src/
│       └── simulator.py        # AODV, disaster triggers, drones
├── dashboard/              # React frontend
│   └── src/
│       ├── components/         # Map, panels, controls
│       └── hooks/              # Socket.IO hook
├── mqtt-broker/            # Mosquitto config
└── docker-compose.yml      # Orchestrates all 7 services
```

---

## Tech Stack

**Backend** — Python 3.11, Flask 3.0, TensorFlow 2.16, PyTorch 2.12, Stable-Baselines3, Gymnasium, kyber-py, pycryptodome, paho-mqtt, NetworkX

**Frontend** — React 18, Leaflet.js, Socket.IO, Recharts, Axios

**Infrastructure** — Docker Compose, Eclipse Mosquitto 2.0, nginx

---

<div align="center">

Made with purpose for Smart India · B.Tech Computer Networks · 2025

</div>
