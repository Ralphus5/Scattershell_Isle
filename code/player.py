"""Functions are sorted according to execution order."""
from enemy import *

class Player(Entity):
    def __init__(self, game: Game, pos: Vector2, textures: list[Texture]) -> None:
        super().__init__(game, 'player', pos, textures)
        self.inventory = Inventory(self.game)
        self.slot_1_item: Optional[str] = self.game.last_saved_slot_1_item
        self.slot_2_item: Optional[str] = self.game.last_saved_slot_2_item
        self.weapon: Optional[SlotItem] = None
        # animation
        self.animation_state = 'down'
        self.facing_direction = 'down'
        # timers
        self.attack_cooldown_timer.original_callback = self.destroy_slot_item
        self.low_health_sfx_timer = Timer(self.game, LOW_HEALTH_SFX_RETRIGGER_DURATION, True, False, False)
        self.timers.append(self.low_health_sfx_timer)
        self.max_health = self.game.last_saved_player_max_health
        self.health = self.game.last_saved_player_current_health

    def update(self, dt: float) -> None:
        if self.health <= 4 and not self.low_health_sfx_timer.active:
            self.low_health_sfx_timer.activate()
            self.game.play_sfx('low_health')
        if not self.knockback_timer.active and not self.attack_cooldown_timer.active:
            if not self.game.fade_to_black_timer.active and not self.game.fade_from_black_timer.active:
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
        if self.knockback_timer.active or self.game.fade_to_black_timer.active or self.game.fade_from_black_timer.active:
            return
        if self.game.input_pressed('item_slot_1') and not self.attack_cooldown_timer.active and self.slot_1_item:
            self.animation_index = 0.0
            self.create_slot_item(self.slot_1_item)
            self.attack_cooldown_timer.activate()
        elif self.game.input_pressed('item_slot_2') and not self.attack_cooldown_timer.active and self.slot_2_item:
            self.animation_index = 0.0
            self.create_slot_item(self.slot_2_item)
            self.attack_cooldown_timer.activate()

    def create_slot_item(self, slot_item: str) -> None:
        match slot_item:
            case 'sword': self.weapon = Sword(self.game)
        assert self.weapon
        self.game.level.sprites.append(self.weapon)

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

    def destroy_slot_item(self) -> None:
        if self.weapon and self.weapon in self.game.level.sprites:
            self.game.level.sprites.remove(self.weapon)
            self.weapon = None

class Inventory:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.slot_items: Set[str] = set(self.game.last_saved_slot_items) if self.game.last_saved_slot_items else set()

        self.item_counts: dict[str, int] = self.game.last_saved_item_counts
