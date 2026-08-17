from utils import *

class Sprite:
    def __init__(self, pos: Vector2, texture: Texture) -> None:
        self.pos = pos
        self.texture = texture

    @property
    def y_sort_pos(self) -> float:
        return self.pos.y + self.texture.height

    def update(self, dt: float) -> None:
        pass

    def draw(self):
        draw_texture_ex(self.texture, self.pos, 0, 1, WHITE)

class Tile(Sprite):
    def __init__(self, pos: Vector2, texture: Texture, hitbox_height_ratio: float = 0.85) -> None:
        super().__init__(pos, texture)
        
        # Hitbox belegt nur die unteren X% des Sprites (z. B. 35% für den Sockel)
        hitbox_h = self.texture.height * hitbox_height_ratio
        hitbox_y = self.pos.y + (self.texture.height - hitbox_h)
        
        self.hitbox = Rectangle(self.pos.x, hitbox_y, self.texture.width, hitbox_h)

class Zone():
    def __init__(self, dimensons: Rectangle|Circle, name: str, player_pos: str, shape: str) -> None:
        self.shape = dimensons
        self.name = name
        self.player_pos = player_pos
        self.type = shape