from GameData.ConnectionHandler import ConnectionHandler
from GameData.GameEngine import GameEngine
from GameData.Action import Action

import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging

app = Flask(__name__)
socketio = SocketIO(app)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def authenticate(username, password):
    # TODO: Implement authentication
    if password == "foobar":
        return True
    return False


@socketio.on('authentication')
def handle_authentication(data):
    session_id = request.sid
    username = data['username']
    password = data['password']
    if authenticate(username, password):
        connection_handler.add_player(username, session_id)
        game_engine.add_player(connection_handler.get_player(username))
        socketio.emit('authenticated', {"status": "success"})
    else:
        socketio.emit('unauthorized', {"status": "failure"})


@socketio.on('connect')
def handle_connect():
    print("Client connected")


@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    connection_handler.remove_player_by_session(session_id)
    print("Client disconnected")


@socketio.on('action')
def handle_action(data):
    session_id = request.sid
    player = connection_handler.get_player_by_session(session_id)
    if player:
        action = Action(player, data['action'])
        game_engine.add_action(action)


if __name__ == "__main__":
    connection_handler = ConnectionHandler()
    game_engine = GameEngine(socketio)
    threading.Thread(target=game_engine.run, daemon=True).start()
    socketio.run(app)
