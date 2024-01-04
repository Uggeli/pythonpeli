from PIL import Image
import gzip

from .Entities import Entity
from .EventHub import EventHub, Event  # noqa: F401
from .Action import Action


class Manager:
    def __init__(self, config, event_hub: EventHub = None) -> None:
        self.config = config
        self.event_hub = event_hub
        self.event_queue = []
        self.setup()

    def setup(self):
        """Add event listeners here and do any other setup"""
        raise NotImplementedError

    def OnEvent(self, event: Event):
        self.event_queue.append(event)

    def OnDirectEvent(self, event_name, data):
        """Pass queue handling logic here"""
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class MapChunk:
    pass


class MapManager(Manager):
    """
    Handles mapdata, collisions, and entity spawning.
    """
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

    Entities = []

    def __init__(self, config, event_hub: EventHub = None) -> None:
        super().__init__(config, event_hub)

    def setup(self):
        print("Setting up map manager")
        self.event_hub.add_listener('CollisionCheck', self.OnEvent)
        self.event_hub.add_listener('Spawn', self.OnEvent)
        self.event_hub.add_listener('Despawn', self.OnEvent)

    def update(self):
        for event in self.event_queue:
            if not isinstance(event, Event):
                print(f"Error: {event} is not an instance of Event")
                continue
            try:
                print(f"Handling event {event.name}")
                if event.name == 'CollisionCheck':
                    self.handle_collision_check(event)
                elif event.name == 'Spawn':
                    self.handle_spawn(event)
                elif event.name == 'Despawn':
                    self.handle_despawn(event)
            except Exception as e:
                event.update_status(-1)  # it clearly failed
                print(f"Error handling event {event.name}: {e}")
        self.event_queue = []

    def handle_despawn(self, event: Event):
        result = self.Despawn(event.data)
        event.update_status(1 if result else -1)
        if event.callback:
            event.callback(event)

    def handle_collision_check(self, event: Event):
        result = self.CollisionCheck(event.data)
        event.update_status(1 if result else -1)
        if event.callback:
            event.callback(event)

    def handle_spawn(self, event: Event):
        result = self.Spawn(event.data)
        event.update_status(1 if result else -1)
        if event.callback:
            event.callback(event)

    def CheckBounds(self, location):
        if (location[0] < 0 or location[0] > len(self.DUMMY_MAP[0]) - 1 or
                location[1] < 0 or location[1] > len(self.DUMMY_MAP) - 1):
            return False
        return True

    def CollisionCheck(self, data):
        # entity = data['entity']
        location = data['position']
        if self.DUMMY_MAP[location[1]][location[0]] == 0:
            return True
        return False

    def Spawn(self, data):
        entity = data['entity']
        location = data['position']
        print(f"Spawning {entity.name} at {location}")
        if self.CheckBounds(location):
            self.DUMMY_MAP[location[1]][location[0]] = entity
            self.UpdateEntity(entity, location)
            self.Entities.append(entity)
            return True
        return False

    def Despawn(self, data):
        entity = data['entity']
        print(f"Despawning {entity.name} from {entity.local_position}")
        if entity in self.Entities:
            self.DUMMY_MAP[entity.local_position[1]][entity.local_position[0]] = 0
            self.Entities.remove(entity)
            return True
        return False

    def UpdateEntity(self, entity, location):
        if not entity.local_position:
            entity.local_position = location
        self.DUMMY_MAP[entity.local_position[1]][entity.local_position[0]] = 0
        self.DUMMY_MAP[location[1]][location[0]] = entity
        entity.local_position = location

    def GetChunk(self, chunkPosition: tuple):
        pass

    def GetMapData(self, chunkPosition: tuple, EntityPosition: tuple):
        pass

    def get_gamestate(self, player):
        # Get player position
        if player:
            viewport = self.get_viewport_variable_size(player)
            return viewport
        return None

    def get_viewport_variable_size(self, player, radious=6):
        if player:
            x, y = player.local_position
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
                            entity = entity.to_dict()
                        row.append(entity)
                    else:
                        row.append('w')
                viewport["tiles"].append(row)
            return viewport
        return None

    def check_bounds(self, x, y):  # returns true if in bounds
        if x < 0 or x > len(self.DUMMY_MAP[0]) - 1 or y < 0 or y > len(self.DUMMY_MAP) - 1:
            return False
        return True


class Texture:
    def __init__(self):
        self.texture_type = None
        self.data = None
        self.name = None
        self.size = None


class TextureManager(Manager):
    def __init__(self, config, event_hub: EventHub = None) -> None:
        super().__init__(config, event_hub)
        self.textures = {}
        for texture_name, texture in self.config['TextureManager'].items():
            try:
                self.loadTexture(texture_name, texture)
            except Exception as e:
                print(f'Error loading texture {texture_name}: {e}')

    def setup(self):
        print("Setting up texture manager")
        self.event_hub.add_listener('GetTexture', self.OnEvent)

    def update(self):
        for event in self.event_queue:
            if event.name == 'GetTexture':
                self.handle_get_texture(event)
        self.event_queue = []

    def handle_get_texture(self, event: Event):
        texture_name = event.data
        texture = self.getTexture(texture_name)
        event.update_status(1 if texture else -1)
        if event.callback:
            event.callback(event)

    def loadTexture(self, texture_name, texture):
        if texture['type'] == 'texture':
            with open(texture['path'], 'rb') as f:
                tx = Texture()
                tx.texture_type = 'texture'
                tx.data = self.compressTexture(f.read())
                tx.name = texture_name
                tx.size = (texture['h_texture'], texture['v_texture'])
                self.textures[texture_name] = tx

        elif texture['type'] == 'spritesheet':
            texture_width = texture['h_texture']  # Horizontal dimension of the entire texture
            texture_height = texture['v_texture']  # Vertical dimension of the entire texture

            sprite_width = texture['h_spritesheet']  # Horizontal dimension of each sprite
            sprite_height = texture['v_spritesheet']  # Vertical dimension of each sprite

            sprites_x = texture_width // sprite_width
            sprites_y = texture_height // sprite_height

            with Image.open(texture['path']) as img:
                for y in range(sprites_y):
                    for x in range(sprites_x):
                        tx = Texture()
                        tx.texture_type = 'texture'
                        cropped_img = img.crop((x * sprite_width, y * sprite_height,
                                               (x + 1) * sprite_width, (y + 1) * sprite_height))
                        # tx.data = self.compressTexture(cropped_img.tobytes())
                        tx.data = cropped_img
                        tx.name = f'{texture_name}_{x}_{y}'
                        tx.size = (sprite_width, sprite_height)
                        self.textures[tx.name] = tx

        elif texture['type'] == 'animation':
            # Animation handling logic here
            pass

    def compressTexture(self, textureData):
        try:
            return gzip.compress(textureData)
        except Exception as e:
            print(f'Error compressing texture: {e}')
            return None

    def getTexture(self, texture_name):
        # quick and dirty
        texture_name_map = {
            0: 'spritesheet_0_0',
            'w': 'spritesheet_0_1',
        }
        texture_name = texture_name_map.get(texture_name, 'spritesheet_0_0')
        try:
            return self.textures[texture_name]
        except KeyError:
            print(f'Texture {texture_name} not found')
            return None


class ActionManager(Manager):
    def __init__(self, event_hub: EventHub):
        self.actions = []
        self.event_hub = event_hub

    def create_action(self, data):
        action_handlers = {
            "Move": self.handle_move,
            "Attack": self.handle_attack,
            "Spawn": self.handle_spawn,
            "Despawn": self.handle_despawn
        }
        action = data.get('action')
        if action in action_handlers:
            action_handlers[action](data)
        else:
            # Handle unknown action
            pass

    def handle_move(self, data):
        # Logic for handling move action
        pass

    def handle_attack(self, data):
        # Logic for handling attack action
        pass

    def handle_spawn(self, data):
        print("Handling spawn action")
        entity = data['entity']
        position = data['position']
        required_events = [
            {'event_name': 'CollisionCheck', 'data': {'entity': entity, 'position': position}},
            {'event_name': 'Spawn', 'data': {'entity': entity, 'position': position}}
        ]
        self.actions.append(Action("Spawn", required_events, self.event_hub))
        print(f'Spawn action created for {entity.name} at {position}')

    def handle_despawn(self, data):
        print("Handling despawn action")
        entity = data['entity']
        required_events = [
            {'event_name': 'Despawn', 'data': {'entity': entity}}
        ]
        self.actions.append(Action("Despawn", required_events, self.event_hub))
        print(f'Despawn action created for {entity.name}')

    def remove_action(self, action: Action):
        self.actions.remove(action)

    def update(self):
        for action in self.actions[:]:
            action.execute()
            if action.complete or action.failed:
                self.actions.remove(action)


class GameStateManager(Manager):
    pass
