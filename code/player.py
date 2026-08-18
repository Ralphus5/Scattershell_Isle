from sprites import *

class Player(Sprite):
    def __init__(self, game: Game, pos: Vector2, texture: Texture) -> None:
        self.game = game
        super().__init__(pos, texture)
        self.direction = Vector2()
        self.speed = PLAYER_SPEED
        self.half_hitbox_offset = PLAYER_HITBOX_OFFSET / 2
        self.hitbox = inflate_rect(Rectangle(self.pos.x, self.pos.y + self.half_hitbox_offset, self.texture.width, self.texture.height), 0, -PLAYER_HITBOX_OFFSET)

    @property
    def center(self) -> Vector2:
        return Vector2(self.pos.x + self.texture.width/2, self.pos.y + self.texture.height/2)   

    def update(self, dt: float) -> None:
        self.move(dt)

    def set_position(self, pos: Vector2) -> None:
        self.pos = Vector2(pos.x, pos.y)
        self.hitbox.x = self.pos.x
        self.hitbox.y = self.pos.y + self.half_hitbox_offset

    def move(self, dt: float) -> None:
        self.direction = self.game.input_manager.get_player_movement_input()
        if vector2_length(self.direction) > 1:
            self.direction = vector2_normalize(self.direction)

        # --- Horizontal ---
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.x = self.pos.x
        self.collisions('horizontal')
        
        # --- Vertical ---
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.y = self.pos.y + self.half_hitbox_offset
        self.collisions('vertical')

    def collisions(self, direction: str) -> None:
        if direction == 'horizontal':
            for collision_box in self.game.state_manager.level.collision_boxes:
                if check_collision_recs(self.hitbox, collision_box):
                    if self.direction.x > 0:
                        self.hitbox.x = collision_box.x - self.hitbox.width 
                    elif self.direction.x < 0:
                        self.hitbox.x = collision_box.x + collision_box.width
            self.pos.x = self.hitbox.x

        if direction == 'vertical':
            for collision_box in self.game.state_manager.level.collision_boxes:
                if check_collision_recs(self.hitbox, collision_box):
                    if self.direction.y > 0:
                        self.hitbox.y = collision_box.y - self.hitbox.height
                    elif self.direction.y < 0:
                        self.hitbox.y = collision_box.y + collision_box.height
            self.pos.y = self.hitbox.y - self.half_hitbox_offset
