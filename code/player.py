from enemy import *

class Player(Entity):
    def __init__(self, game: Game, pos: Vector2, textures: list[Texture]) -> None:
        super().__init__(game, 'player', pos, textures)
        self.sword = None
        # animation
        self.animation_state = 'down'
        self.facing_direction = 'down'
        # attributes
        self.health = ENTITY_DATA[self.obj_name]['health']
        self.speed = ENTITY_DATA[self.obj_name]['speed']
        self.damage = cast(int, ENTITY_DATA[self.obj_name]['damage'])
        self.knockback = cast(int, ENTITY_DATA[self.obj_name]['knockback'])
        # timers
        self.attack_cooldown_timer = Timer(self.game, ENTITY_DATA[self.obj_name]['attack_cooldown'], True, False, False, self.destroy_weapon)
        self.timers.append(self.attack_cooldown_timer)

    def update(self, dt: float) -> None:
        if not self.knockback_timer.active:
            self.direction = self.game.get_player_movement_input()
            if vector2_length(self.direction) > 1:
                self.direction = vector2_normalize(self.direction)
        super().update(dt)

    def set_position(self, pos: Vector2) -> None:
        self.pos = Vector2(pos.x, pos.y)
        self.hitbox.x = self.pos.x + self.half_hitbox_offset_horizontal
        self.hitbox.y = self.pos.y + self.half_hitbox_offset_vertical

    def attack(self) -> None:
        if self.knockback_timer.active:
            return
        if (self.game.input_pressed('attack') or is_mouse_button_pressed(0)) and not self.attacking:
            self.attacking = True
            self.animation_index = 0.0
            self.create_weapon()
            self.attack_cooldown_timer.activate()
        if not self.attack_cooldown_timer.active:
            self.attacking = False

    def create_weapon(self) -> None:
        texture = self.game.sword_images[self.facing_direction]

        match(self.facing_direction):
            case 'down':
                spawn_pos = Vector2(self.pos.x + self.texture.width/8, self.pos.y + self.texture.height)
            case 'up': 
                spawn_pos = Vector2(self.pos.x + self.texture.width/8, self.pos.y - texture.height)
            case 'right': 
                spawn_pos = Vector2(self.pos.x + self.texture.width, self.center.y)
            case 'left': 
                spawn_pos = Vector2(self.pos.x - texture.width, self.center.y)

        self.sword = Weapon(self.game, 'sword', spawn_pos, texture)
        self.game.level.sprites.append(self.sword)

    def destroy_weapon(self) -> None:
        for sprite in self.game.level.sprites:
            if sprite.__class__ == Weapon:
                self.sword = None
                self.game.level.sprites.remove(sprite)

    def update_appearance(self, dt: float) -> None:
        # --- Persist current facing direction if its input key is still held ---
        if not self.knockback_timer.active:
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
        self.animation_frames = self.game.entity_images['player'][self.animation_state]
        self.animation_index += PLAYER_ANIMATION_SPEED * self.speed * dt
        super().update_appearance(dt)
