"""
In-memory network topology for the disaster mesh.
Nodes represent ground RPi units + drone UAVs.
Edges represent active mesh links.
"""
import time
import random
import networkx as nx

# Node types
TYPE_GROUND = "ground"
TYPE_DRONE  = "drone"
TYPE_SDN    = "sdn"

_graph = nx.Graph()
_node_meta: dict = {}


def _init_topology():
    nodes = [
        ("N1",  {"type": TYPE_GROUND, "lat": 28.613,  "lon": 77.209,  "status": "online",  "load": 0.2}),
        ("N2",  {"type": TYPE_GROUND, "lat": 28.618,  "lon": 77.220,  "status": "online",  "load": 0.3}),
        ("N3",  {"type": TYPE_GROUND, "lat": 28.608,  "lon": 77.230,  "status": "online",  "load": 0.4}),
        ("N4",  {"type": TYPE_GROUND, "lat": 28.600,  "lon": 77.215,  "status": "online",  "load": 0.25}),
        ("N5",  {"type": TYPE_GROUND, "lat": 28.623,  "lon": 77.200,  "status": "online",  "load": 0.15}),
        ("N6",  {"type": TYPE_GROUND, "lat": 28.595,  "lon": 77.240,  "status": "online",  "load": 0.35}),
        ("N7",  {"type": TYPE_GROUND, "lat": 28.630,  "lon": 77.235,  "status": "online",  "load": 0.10}),
        ("N8",  {"type": TYPE_GROUND, "lat": 28.590,  "lon": 77.205,  "status": "online",  "load": 0.45}),
        ("D1",  {"type": TYPE_DRONE,  "lat": 28.614,  "lon": 77.218,  "status": "standby", "load": 0.0}),
        ("D2",  {"type": TYPE_DRONE,  "lat": 28.605,  "lon": 77.222,  "status": "standby", "load": 0.0}),
        ("SDN", {"type": TYPE_SDN,    "lat": 28.610,  "lon": 77.212,  "status": "online",  "load": 0.5}),
    ]

    edges = [
        ("N1", "N2", 0.1), ("N1", "N5", 0.12), ("N1", "SDN", 0.05),
        ("N2", "N3", 0.15), ("N2", "N7", 0.2),
        ("N3", "N6", 0.18), ("N3", "N4", 0.1),
        ("N4", "N8", 0.14), ("N4", "SDN", 0.08),
        ("N5", "N7", 0.1),
        ("N6", "N8", 0.12),
        ("N7", "SDN", 0.07),
    ]

    for node_id, meta in nodes:
        _graph.add_node(node_id)
        _node_meta[node_id] = {**meta, "id": node_id, "last_seen": time.time()}

    for src, dst, weight in edges:
        _graph.add_edge(src, dst, weight=weight, active=True)


_init_topology()


def get_topology() -> dict:
    nodes = []
    for n in _graph.nodes:
        m = _node_meta[n]
        nodes.append({
            "id": n,
            "type": m["type"],
            "lat": m["lat"],
            "lon": m["lon"],
            "status": m["status"],
            "load": round(m["load"], 2),
        })

    edges = []
    for u, v, data in _graph.edges(data=True):
        edges.append({
            "source": u,
            "target": v,
            "weight": round(data.get("weight", 0.1), 3),
            "active": data.get("active", True),
        })

    return {"nodes": nodes, "edges": edges, "timestamp": time.time()}


def kill_node(node_id: str):
    if node_id in _node_meta:
        _node_meta[node_id]["status"] = "offline"
        for u, v, data in _graph.edges(node_id, data=True):
            data["active"] = False
        return True
    return False


def restore_node(node_id: str):
    if node_id in _node_meta:
        _node_meta[node_id]["status"] = "online"
        for u, v, data in _graph.edges(node_id, data=True):
            data["active"] = True
        return True
    return False


def deploy_drone(drone_id: str, lat: float, lon: float, connect_to: list[str]):
    if drone_id not in _node_meta:
        return False
    meta = _node_meta[drone_id]
    meta["status"] = "active"
    meta["lat"] = lat
    meta["lon"] = lon
    for target in connect_to:
        if target in _graph.nodes:
            _graph.add_edge(drone_id, target, weight=0.25, active=True)
    return True


def get_best_path(src: str, dst: str) -> list[str]:
    try:
        active_nodes = [n for n, m in _node_meta.items() if m["status"] != "offline"]
        sub = _graph.subgraph(active_nodes)
        return nx.shortest_path(sub, src, dst, weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []


def tick_simulation():
    """Slightly randomise node loads to simulate live traffic."""
    for node_id, meta in _node_meta.items():
        if meta["status"] == "online":
            delta = random.uniform(-0.03, 0.03)
            meta["load"] = max(0.0, min(1.0, meta["load"] + delta))
