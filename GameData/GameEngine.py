import json
import random
import time

from flask_socketio import SocketIO
from GameData.Entities import Entity
from GameData.Action import Action
from GameData.EventHub import EventHub, Event  # noqa: F401


class GameEngine:
    DUMMY_MAP = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 'w', 'w', 'w', 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    players = []
    actions = []

    def __init__(self, socketio: SocketIO, event_hub: EventHub, config):
        self.socketio = socketio
        self.EventHub = event_hub
        self.config = config
        self.EventHub.add_listener("move", self.add_action)

        # init Managers
        

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

        for player in self.players:
            game_state = self.get_viewport_variable_size(player)
            self.socketio.emit('gameStateUpdate', json.dumps(game_state))  # Convert game_state to a JSON string
            # socketio.emit('gameStateUpdate', jsonify(game_state))

    def get_gamestate(self, player):
        # Get player position
        player_entity = self.get_player(player)
        if player_entity:
            x, y = player_entity.position
            # Get viewport
            viewport = {"tiles": [], "position": (x, y)}

            # Player can see 3x3 grid around them
            for j in range(y - 1, y + 2):
                row = []
                for i in range(x - 1, x + 2):
                    if self.check_bounds(i, j):
                        # Convert entity to a serializable format if necessary
                        entity = self.DUMMY_MAP[j][i]
                        if isinstance(entity, Entity):
                            entity = entity.to_dict()  # Assuming Entity has a method to convert to dictionary
                        row.append(entity)
                    else:
                        row.append('w')  # If out of bounds, return wall
                viewport["tiles"].append(row)
            return viewport
        return None

    def get_viewport_variable_size(self, player, radious=6):
        player_entity = self.get_player(player)
        if player_entity:
            x, y = player_entity.position
            # Get viewport
            viewport = {"tiles": [], "position": (x, y)}

            # Player can see 3x3 grid around them
            for j in range(y - radious, y + radious + 1):
                row = []
                for i in range(x - radious, x + radious + 1):
                    if self.check_bounds(i, j):
                        # Convert entity to a serializable format if necessary
                        entity = self.DUMMY_MAP[j][i]
                        if isinstance(entity, Entity):
                            entity = entity.to_dict()  # Assuming Entity has a method to convert to dictionary
                        row.append(entity)
                    else:
                        row.append('w')
                viewport["tiles"].append(row)
            return viewport
        return None
