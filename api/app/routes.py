from flask import Blueprint, jsonify, request
from .topology import (
    get_topology, kill_node, restore_node,
    deploy_drone, get_best_path,
)

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/topology")
def topology():
    return jsonify(get_topology())


@bp.post("/node/<node_id>/kill")
def node_kill(node_id):
    ok = kill_node(node_id)
    return jsonify({"ok": ok, "node": node_id, "action": "killed"})


@bp.post("/node/<node_id>/restore")
def node_restore(node_id):
    ok = restore_node(node_id)
    return jsonify({"ok": ok, "node": node_id, "action": "restored"})


@bp.post("/drone/deploy")
def drone_deploy():
    data = request.json or {}
    drone_id   = data.get("drone_id", "D1")
    lat        = data.get("lat", 28.614)
    lon        = data.get("lon", 77.218)
    connect_to = data.get("connect_to", [])
    ok = deploy_drone(drone_id, lat, lon, connect_to)
    return jsonify({"ok": ok, "drone": drone_id})


@bp.get("/path")
def path():
    src = request.args.get("src", "N1")
    dst = request.args.get("dst", "N6")
    route = get_best_path(src, dst)
    return jsonify({"src": src, "dst": dst, "path": route})


@bp.get("/health")
def health():
    return jsonify({"status": "ok"})
