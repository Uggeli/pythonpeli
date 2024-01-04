class Entity:
    local_position = None  # in tiles
    world_position = None  # in chunks
    name = None
    session_id = None
    color = None

    def __init__(self, name, position, color):
        self.name = name
        self.local_position = position
        self.color = color

    def move(self, x, y):
        self.position = (x, y)

    def __str__(self):
        return f"{self.name} at {self.local_position}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __hash__(self):
        return hash(self.name)

    def to_dict(self):
        return {
            "name": self.name,
            "position": self.local_position,
            "color": self.color
        }
