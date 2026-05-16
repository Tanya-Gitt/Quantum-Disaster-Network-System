"""
WebSocket event handlers — push live topology updates to the dashboard.
"""
import eventlet
from flask_socketio import emit
from .topology import get_topology, tick_simulation

_broadcast_greenlet = None


def _broadcast_loop(sio):
    while True:
        eventlet.sleep(2)
        tick_simulation()
        sio.emit("topology_update", get_topology(), namespace="/")


def register_events(sio):
    global _broadcast_greenlet

    @sio.on("connect")
    def on_connect():
        emit("topology_update", get_topology())

    @sio.on("request_topology")
    def on_request():
        emit("topology_update", get_topology())

    @sio.on("sos_broadcast")
    def on_sos(data):
        sio.emit("sos_alert", data)

    if _broadcast_greenlet is None:
        _broadcast_greenlet = eventlet.spawn(_broadcast_loop, sio)
