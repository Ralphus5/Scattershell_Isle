from sprites import *

class Player(Sprite):
    def __init__(self, game: Game, pos: Vector2, textures: list[Texture]) -> None:
        self.game = game
        super().__init__(pos, textures[0])
        # animation
        self.animation_frames = textures
        self.animation_index: float = 0.0
        self.animation_state = 'down'
        self.facing_direction = 'down'
        self.attacking = False
        # timers
        self.timers: list[Timer] = []
        self.attack_cooldown_timer = Timer(self.game, PLAYER_ATTACK_COOLDOWN, True, False, False)
        self.timers.append(self.attack_cooldown_timer)
        # attributes
        self.direction = Vector2()
        self.speed = PLAYER_SPEED
        # hitbox
        self.half_hitbox_offset = PLAYER_HITBOX_OFFSET / 2
        self.hitbox = inflate_rect(Rectangle(self.pos.x, self.pos.y + self.half_hitbox_offset, self.texture.width, self.texture.height), 0, -PLAYER_HITBOX_OFFSET)

    @property
    def center(self) -> Vector2:
        return Vector2(self.pos.x + self.texture.width/2, self.pos.y + self.texture.height/2)
     
    def set_position(self, pos: Vector2) -> None:
        self.pos = Vector2(pos.x, pos.y)
        self.hitbox.x = self.pos.x
        self.hitbox.y = self.pos.y + self.half_hitbox_offset

    def update(self, dt: float) -> None:
        for timer in self.timers:
            timer.update()
        self.attack(dt)
        self.move(dt)
        self.update_appearance(dt)

    def attack(self, dt: float) -> None:
        if self.game.input_manager.pressed('attack') and not self.attacking:
            self.attacking = True
            self.animation_index = 0.0
            self.attack_cooldown_timer.activate()
        if not self.attack_cooldown_timer.active:
            self.attacking = False
            
    def move(self, dt: float) -> None:
        if self.attacking:
            return
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

    def update_appearance(self, dt: float) -> None:
        # --- Persist current facing direction if its input key is still held ---
        still_holding_current = (
            (self.facing_direction == 'down' and self.direction.y > 0) or
            (self.facing_direction == 'up' and self.direction.y < 0) or
            (self.facing_direction == 'right' and self.direction.x > 0) or
            (self.facing_direction == 'left' and self.direction.x < 0)
        )

        # If the active facing direction was released, pivot to any remaining active input
        if not still_holding_current:
            if self.direction.y > 0:
                self.facing_direction = 'down'
            elif self.direction.y < 0:
                self.facing_direction = 'up'
            elif self.direction.x > 0:
                self.facing_direction = 'right'
            elif self.direction.x < 0:
                self.facing_direction = 'left'

        # --- Construct state key ---
        base_state = self.facing_direction

        if self.attacking:
            self.animation_state = f"{base_state}_attack"
        elif vector2_length(self.direction) == 0:
            self.animation_state = f"{base_state}_idle"
        else:
            self.animation_state = base_state

        # --- Update texture frame ---
        self.animation_frames = self.game.player_images[self.animation_state]
        self.animation_index += PLAYER_ANIMATION_SPEED * dt
        self.texture = self.animation_frames[int(self.animation_index) % len(self.animation_frames)]