import json
import random
import time

from flask_socketio import SocketIO
from GameData.Entities import Entity
from GameData.Action import Action
from GameData.EventHub import EventHub, Event  # noqa: F401
from GameData.Managers import MapManager, TextureManager, MovementManager, SpawnManager, CollisionManager


class GameEngine:
    players = []
    actions = []

    def __init__(self, socketio: SocketIO, event_hub: EventHub, config):
        self.socketio = socketio
        self.EventHub = event_hub
        self.config = config
        self.EventHub.add_listener("move", self.add_action)

        # init Managers
        self.MapManager = MapManager(self.config)
        self.TextureManager = TextureManager(self.config)
        self.MovementManager = MovementManager(self.config)
        self.SpawnManager = SpawnManager(self.config)
        self.CollisionManager = CollisionManager(self.config)

        # init EventHub
        self.EventHub.add_listener("move", self.MovementManager.OnMoveRequest)
        self.EventHub.add_listener("collide", self.CollisionManager.OnCollide)
        self.EventHub.add_listener("spawn", self.SpawnManager.OnSpawn)

    def move(self, entity, direction):
        x, y = entity.position
        if direction == "up":
            y -= 1
        elif direction == "down":
            y += 1
        elif direction == "left":
            x -= 1
        elif direction == "right":
            x += 1
        if self.check_collision(x, y):
            # update map
            self.DUMMY_MAP[entity.position[1]][entity.position[0]] = 0
            self.DUMMY_MAP[y][x] = entity
            # update entity
            entity.position = (x, y)
            return True
        return False

    def add_player(self, player: Entity):
        if not self.get_player(player):
            # add player to map
            x, y = player.position
            timeoutCounter = 0
            while not self.check_collision(x, y) and timeoutCounter < 100:
                timeoutCounter += 1
                x = random.randint(0, len(self.DUMMY_MAP[0]) - 1)
                y = random.randint(0, len(self.DUMMY_MAP) - 1)
            if timeoutCounter < 100:
                print(f"Player {player.name} spawned at {x}, {y}")
                self.DUMMY_MAP[y][x] = player
                player.position = (x, y)
                self.players.append(player)
            else:
                print(f"Player {player.name} could not be spawned")

    def remove_player(self, player: Entity):
        if self.get_player(player):
            self.players.remove(self.get_player(player))
            x, y = player.position
            self.DUMMY_MAP[y][x] = 0

    def get_player(self, player: Entity):
        for p in self.players:
            if p == player:
                return p
        return None

    def get_player_by_name(self, player_name: str) -> Entity:
        for p in self.players:
            if p.name == player_name:
                return p
        return None

    def add_action(self, action: Action):
        if action.action == "move":
            self.actions.append((self.move, (action.actor, action.target)))

    def run(self):
        while True:
            self.update()
            time.sleep(0.016)  # 16ms for game logic update

    def check_bounds(self, x, y):  # returns true if in bounds
        if x < 0 or x > len(self.DUMMY_MAP[0]) - 1 or y < 0 or y > len(self.DUMMY_MAP) - 1:
            return False
        return True

    def check_collision(self, x, y):  # returns true if no collision
        if not self.check_bounds(x, y):
            return False
        if self.DUMMY_MAP[y][x] != 0:
            return False
        return True

    def update(self):
        for action, args in self.actions:
            action(*args)
        self.actions = []

        # Update players
        for player in self.players:
            game_state = self.MapManager.get_viewport_variable_size(player)
            self.socketio.emit('gameStateUpdate', json.dumps(game_state))  # Convert game_state to a JSON string
            # socketio.emit('gameStateUpdate', jsonify(game_state))

