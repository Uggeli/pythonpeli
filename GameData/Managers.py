from .Entities import Entity


class MovementManager:
    def OnMoveRequest(self, direction):
        pass


class CollisionManager:
    def OnCollide(self, entity1: Entity, entity2):
        pass