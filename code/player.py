"""Functions are sorted according to execution order."""
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
        self.attack_cooldown_timer.callback = self.destroy_weapon

    def update(self, dt: float) -> None:
        if not self.knockback_timer.active and not self.attack_cooldown_timer.active:
            self.direction = self.game.get_player_movement_input()
            if vector2_length(self.direction) > 1:
                self.direction = vector2_normalize(self.direction)
            self.update_facing_direction()
        super().update(dt)
        
    def update_facing_direction(self) -> None:
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

    def attack(self) -> None:
        if self.knockback_timer.active:
            return
        if (self.game.input_pressed('item_slot_1') or is_mouse_button_pressed(0)) and not self.attack_cooldown_timer.active:
            self.animation_index = 0.0
            self.create_weapon()
            self.attack_cooldown_timer.activate()

    def create_weapon(self) -> None:
        self.sword = Sword(self.game, 'sword')
        texture = self.game.sword_images[self.facing_direction]
        self.game.level.sprites.append(self.sword)

    def update_appearance(self, dt: float) -> None:
        # --- Construct state key ---
        base_state = self.facing_direction

        if self.attack_cooldown_timer.active:
            self.animation_state = f"{base_state}_attack"
        elif vector2_length(self.direction) == 0:
            self.animation_state = f"{base_state}_idle"
        else:
            self.animation_state = base_state

        # --- Update texture frame ---
        self.animation_frames = self.game.entity_images['player'][self.animation_state]
        self.animation_index += PLAYER_ANIMATION_SPEED * self.speed * dt
        super().update_appearance(dt)

    def destroy_weapon(self) -> None:
        if self.sword:
            self.game.level.sprites.remove(self.sword)
            self.sword = None
