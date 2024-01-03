import json
import time
from queue import Queue
from flask_socketio import SocketIO
from GameData.EventHub import EventHub, Event  # noqa: F401
from GameData.Managers import MapManager, TextureManager, ActionManager


class GameEngine:
    def __init__(self, socketio: SocketIO, event_hub: EventHub, config):
        self.socketio = socketio
        self.event_hub = event_hub
        self.config = config

        # Initialize Managers
        self.map_manager = MapManager(config, event_hub)
        self.texture_manager = TextureManager(config, event_hub)
        self.action_manager = ActionManager(event_hub)
        self.managers = [self.map_manager, self.texture_manager, self.action_manager]

        self.actions = Queue()

    def get_textures(self, data):
        return [
            self.texture_manager.getTexture(texture)
            for texture in data
            if self.texture_manager.getTexture(texture)
        ]

    def run(self):
        previous_time = time.time()
        while True:
            current_time = time.time()
            delta = current_time - previous_time
            if delta >= 0.016:  # 60 fps
                self.update_players()
                previous_time = current_time

            self.process_actions()
            self.update_managers()

    def process_actions(self):
        while not self.actions.empty():
            action, args = self.actions.get()
            try:
                action(*args)
            except Exception as e:
                print(f"Error processing action: {e}")

    def update_managers(self):
        for manager in self.managers:
            try:
                manager.update()
            except Exception as e:
                print(f"Error updating manager {type(manager).__name__}: {e}")

    def update_players(self):
        for player in self.map_manager.Entities:
            try:
                game_state = self.map_manager.get_gamestate(player)
                self.socketio.emit('gameStateUpdate', json.dumps(game_state))
            except Exception as e:
                print(f"Error updating player {player}: {e}")
