import random
from GameData.Entities import Entity


class ConnectionHandler:
    colours = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown",]
    connected_players = {}
    players = []  # Entity objects

    def add_player(self, player, session_id):
        if player not in self.connected_players:
            self.connected_players[player] = session_id
            self.players.append(Entity(player, (0, 0), random.choice(self.colours)))
            print(f'{player} connected')

    def remove_player(self, player):
        if player in self.connected_players:
            self.connected_players.pop(player)
            self.players.remove(self.get_player(player))
            print(f'{player} disconnected')

    def get_player(self, player):
        for p in self.players:
            if p.name == player:
                return p
        return None

    def get_player_by_session(self, session_id):
        for player, id in self.connected_players.items():
            if id == session_id:
                return player
        return None

    def remove_player_by_session(self, session_id):
        player = self.get_player_by_session(session_id)
        if player:
            self.remove_player(player)