from PIL import Image
import gzip

from .Entities import Entity


class MovementManager:

    def __init__(self) -> None:
        pass

    def requestRoute(self, entity: Entity, targetPosition: tuple):
        pass

    def OnMoveRequest(self, entity: Entity, direction):
        pass


class CollisionManager:
    def OnCollide(self, entity1: Entity, entity2):
        pass


class SpawnManager:
    def OnSpawn(self, entity: Entity):
        pass


class MapChunk:
    pass


class MapManager:
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

    def __init__(self, config) -> None:
        pass
    
    def GetChunk(self, chunkPosition: tuple):
        pass

    def GetMapData(self, chunkPosition: tuple, EntityPosition: tuple):
        pass
    
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


class Texture:
    def __init__(self):
        self.texture_type = None
        self.data = None
        self.name = None
        self.size = None


class TextureManager:
    def __init__(self, config) -> None:
        self.config = config
        self.textures = {}
        for texture_name, texture in self.config['TextureManager'].items():
            try:
                self.loadTexture(texture_name, texture)
            except Exception as e:
                print(f'Error loading texture {texture_name}: {e}')

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
            with Image.open(texture['path']) as img:
                for tx_y in range(texture['v_spritesheet']):
                    for tx_x in range(texture['h_spritesheet']):
                        left = tx_x * texture['h_texture']
                        top = tx_y * texture['v_texture']
                        right = left + texture['h_texture']
                        bottom = top + texture['v_texture']
                        sprite = self.compressTexture(img.crop((left, top, right, bottom)))
                        sprite_name = texture['sprite_names'][tx_x * texture['h_spritesheet'] + tx_y] or texture_name
                        tx = Texture()
                        tx.texture_type = 'spritesheet'
                        tx.data = sprite
                        tx.name = sprite_name
                        tx.size = (texture['h_texture'], texture['v_texture'])
                        self.textures[sprite_name] = tx

        elif texture['type'] == 'animation':
            # Animation handling logic here
            pass

    def compressTexture(self, textureData):
        return gzip.compress(textureData)

    def getTexture(self, texture_name):
        try:
            return self.textures[texture_name]
        except KeyError:
            print(f'Texture {texture_name} not found')
            return None
