from sprites import *

class Enemy(Entity):
    def __init__(self, game: Game, pos: Vector2, textures: list[Texture], hitbox_offset_v: int, hitbox_offset_h: int) -> None:
        super().__init__(game, pos, textures, hitbox_offset_v, hitbox_offset_h)

    def attack(self, dt: float):
        pass

    def change_appearance(self, dt:float):
        pass