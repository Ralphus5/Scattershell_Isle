"""Functions are sorted according to execution order."""
from sprites import *

class Enemy(Entity):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, textures: list[Texture]) -> None:
        super().__init__(game, obj_name, pos, textures)
        self.state = 'idle'
        self.notice_radius = self.stats['notice_radius']
        self.attack_radius = self.stats['attack_radius']
        self.knockback_timer.callback = self.on_knockback_end

    def on_knockback_end(self) -> None:
        self.speed = self.stats['speed']
        if self.state == 'attack':
            self.state = 'move'
            self.animation_index = 0
        self.direction = Vector2(0,0)

    def draw(self) -> None:
        if self.hurt_timer.active:
            draw_texture_ex(self.texture, self.pos, 0, 1, Color(235, 130, 130, 255))
        else:
            draw_texture_ex(self.texture, self.pos, 0, 1, WHITE)

    def update(self, dt: float) -> None:
        distance, direction = self.get_player_distance_direction()
        self.update_state(distance, direction)
        super().update(dt)

    def get_player_distance_direction(self) -> tuple[float, Vector2]:
        distance_vector = vector2_subtract(self.game.level.player.center, self.center)
        distance = vector2_length(distance_vector)
        direction = vector2_normalize(distance_vector) if abs(distance) > 0 else Vector2()
        return (distance, direction)

    def update_state(self, distance: float, direction: Vector2) -> None:
        if self.knockback_timer.active:
            return

        if self.state == 'attack':
            self.speed = ENTITY_DATA[self.obj_name].get('attack_speed', self.stats['speed'])
            if self.animation_index >= len(self.animation_frames):
                self.attack_cooldown_timer.activate()
                self.animation_index = 0
                self.speed = self.stats['speed'] if not self.knockback_timer.active else ENTITY_DATA[self.obj_name]['knockback_speed']
                self.state = 'move'
            return

        if distance <= self.attack_radius and not self.attack_cooldown_timer.active:
            self.state = 'attack'
            self.game.level.animation_player.create_attack_animation(self.obj_name, self.center)
            self.animation_index = 0
        elif distance <= self.notice_radius:
            self.state = 'move'
            self.direction = direction
        else:
            self.state = 'idle'
            self.direction = Vector2()
    
    def attack(self):
        pass

    def update_appearance(self, dt: float):
        # --- Update texture frame ---
        self.animation_frames = self.game.entity_images[self.obj_name][self.state]
        self.animation_index += ENEMY_ANIMATION_SPEED * self.speed * dt
        super().update_appearance(dt)
