from utils import *

class Sprite:
    def __init__(self, pos: Vector2, texture: Texture) -> None:
        self.pos = pos
        self.texture = texture
        self.hitbox = Rectangle(self.pos.x,self.pos.y,self.texture.width,self.texture.height)

    @property
    def y_sort_pos(self) -> float:
        return self.pos.y + self.texture.height

    def update(self, dt: float) -> None:
        pass

    def draw(self):
        draw_texture_ex(self.texture, self.pos, 0, 1, WHITE)

class Entity(Sprite):
    def __init__(self, game: Game, pos: Vector2, textures: list[Texture], hitbox_offset_v: int, hitbox_offset_h: int) -> None:
        self.game = game
        super().__init__(pos, textures[0])
        self.animation_frames = textures
        self.animation_index: float = 0.0
        self.attacking = False
        self.timers: list[Timer] = []
        self.direction = Vector2()
        self.speed = 0
        self.half_hitbox_offset_vertical = hitbox_offset_v / 2
        self.half_hitbox_offset_horizontal = hitbox_offset_h / 2
        self.hitbox = inflate_rect(Rectangle(self.pos.x + self.half_hitbox_offset_horizontal, self.pos.y + self.half_hitbox_offset_vertical, self.texture.width, self.texture.height), -hitbox_offset_h, -hitbox_offset_v)

    @property
    def center(self) -> Vector2:
        return Vector2(self.pos.x + self.texture.width/2, self.pos.y + self.texture.height/2)

    def update(self, dt: float) -> None:
        for timer in self.timers:
            timer.update()
        self.attack(dt)
        self.move(dt)
        self.update_appearance(dt)

    def attack(self, dt: float):
        pass
   
    def move(self, dt: float) -> None:
        if self.attacking:
            return
        self.direction = self.game.get_player_movement_input()
        if vector2_length(self.direction) > 1:
            self.direction = vector2_normalize(self.direction)

        # --- Horizontal ---
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.x = self.pos.x + self.half_hitbox_offset_horizontal
        self.collisions('horizontal')
        
        # --- Vertical ---
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.y = self.pos.y + self.half_hitbox_offset_vertical
        self.collisions('vertical')

    def collisions(self, direction: str) -> None:
        if direction == 'horizontal':
            for collision_box in self.game.level.collision_boxes:
                if check_collision_recs(self.hitbox, collision_box):
                    if self.direction.x > 0:
                        self.hitbox.x = collision_box.x - self.hitbox.width 
                    elif self.direction.x < 0:
                        self.hitbox.x = collision_box.x + collision_box.width
            self.pos.x = self.hitbox.x - self.half_hitbox_offset_horizontal

        if direction == 'vertical':
            for collision_box in self.game.level.collision_boxes:
                if check_collision_recs(self.hitbox, collision_box):
                    if self.direction.y > 0:
                        self.hitbox.y = collision_box.y - self.hitbox.height
                    elif self.direction.y < 0:
                        self.hitbox.y = collision_box.y + collision_box.height
            self.pos.y = self.hitbox.y - self.half_hitbox_offset_vertical

    def update_appearance(self, dt: float):
        pass

class Tile(Sprite):
    def __init__(self, pos: Vector2, texture: Texture, hitbox_height_ratio: float = 0.9, hitbox_inflation: int = -10) -> None:
        super().__init__(pos, texture)
        
        # Hitbox belegt nur die unteren X% des Sprites
        hitbox_h = self.texture.height * hitbox_height_ratio
        hitbox_y = self.pos.y + (self.texture.height - hitbox_h)
        
        self.hitbox = inflate_rect(Rectangle(self.pos.x, hitbox_y, self.texture.width, hitbox_h), 0, hitbox_inflation)

class Weapon(Sprite):
    def __init__(self, pos: Vector2, texture: Texture, type: str, game: Game) -> None:
        super().__init__(pos, texture)
        self.game = game
        self.type = type # TO BE ADDED!
        self.game.play_sfx(self.type, 0.2)

class Zone():
    def __init__(self, dimensons: Rectangle|Circle, name: str, player_pos: str, shape_type: str) -> None:
        self.shape = dimensons
        self.name = name
        self.player_pos = player_pos
        self.shape_type = shape_type
        