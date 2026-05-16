from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")


def create_app():
    app = Flask(__name__)
    CORS(app)

    from .routes import bp
    app.register_blueprint(bp)

    from .events import register_events
    register_events(socketio)

    socketio.init_app(app)

    from .mqtt_client import start_mqtt
    start_mqtt(socketio)

    return app
