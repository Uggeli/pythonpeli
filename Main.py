import functools
from GameData.ConnectionHandler import ConnectionHandler
from GameData.EventHub import EventHub
from GameData.GameEngine import GameEngine
from GameData.Entities import Entity

import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging

app = Flask(__name__)
socketio = SocketIO(app)
logger = logging.getLogger(__name__)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        session_id = request.sid
        player = connection_handler.get_player_entity_by_session(session_id)
        if player:
            return f(*args, **kwargs)
        else:
            socketio.emit('unauthorized', {"status": "failure"})
    return wrapped


@app.route('/')
def index():
    return render_template('index.html')


def authenticate(username, password):
    # TODO: Implement authentication
    if password == "foobar":
        return True
    return False


def get_spawn_position():
    return (0, 0)


def create_player_entity(username):
    return Entity(username, None, None)


@socketio.on('authentication')
def handle_authentication(data):
    session_id = request.sid
    username = data['username']
    password = data['password']
    if authenticate(username, password):
        player = create_player_entity(username)
        spawn_action_data = {
            'action': 'Spawn',
            'entity': player,
            'position': get_spawn_position()
        }
        connection_handler.add_player(player, session_id)
        game_engine.action_manager.create_action(spawn_action_data)
        socketio.emit('authenticated', {"status": "success"})
    else:
        socketio.emit('unauthorized', {"status": "failure"})


@socketio.on('connect')
def handle_connect():
    print("Client connected")


@socketio.on('disconnect')
@authenticated_only
def handle_disconnect():
    session_id = request.sid
    player = connection_handler.get_player_entity_by_session(session_id)
    if player:
        despawn_action_data = {
            'action': 'Despawn',
            'entity': player,
        }
        game_engine.action_manager.create_action(despawn_action_data)
        connection_handler.remove_player(player)
    print(f"{player.name if isinstance(player, Entity) else 'client'} disconnected")


@socketio.on('action')
@authenticated_only
def handle_action(data):
    session_id = request.sid
    player = connection_handler.get_player_entity_by_session(session_id)
    print(f"Received action from {player.name}: {data}")
    if player:
        pass


@socketio.on('requestTexture')
@authenticated_only
def handle_request_textures(data):
    session_id = request.sid
    player = connection_handler.get_player_entity_by_session(session_id)
    print(f"Received request for {data} textures from {player.name}")
    if player:
        textures = game_engine.get_textures(data)
        socketio.emit('getTexture', textures)


if __name__ == "__main__":
    config = {
            'TextureManager': {
                'spritesheet': {
                    'path': 'GameData/Assets/Textures/tilemap_packed.png',
                    'type': 'spritesheet',
                    'format': 'png',
                    'h_texture': 192,
                    'v_texture': 176,
                    'h_spritesheet': 16,
                    'v_spritesheet': 16,
                },
            }
        }
    connection_handler = ConnectionHandler()
    event_hub = EventHub()
    game_engine = GameEngine(socketio, event_hub, config)
    threading.Thread(target=game_engine.run, daemon=True).start()
    socketio.run(app)
