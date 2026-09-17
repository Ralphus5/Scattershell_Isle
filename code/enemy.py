"""Functions are sorted according to execution order."""
from sprites import *

class Enemy(Entity):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, textures: list[Texture]) -> None:
        super().__init__(game, obj_name, pos, textures)
        self.state = 'idle'
        self.stats = ENTITY_DATA[obj_name]
        self.health = self.stats['health']
        self.speed = self.stats['speed']
        self.damage = cast(int, self.stats['damage'])
        self.notice_radius = self.stats['notice_radius']
        self.attack_radius = self.stats['attack_radius']
        self.attack_cooldown_timer = Timer(self.game, self.stats['attack_cooldown'], True, False, False)
        self.timers.append(self.attack_cooldown_timer)

    def update(self, dt: float) -> None:
        distance, direction = self.get_player_distance_direction()
        self.update_state(distance, direction)
        super().update(dt)

    def get_player_distance_direction(self) -> tuple[float, Vector2]:
        distance_vector = vector2_subtract(self.game.level.player.center, self.center)
        distance = vector2_length(distance_vector)
        direction = vector2_normalize(distance_vector) if distance > 0 else Vector2()
        return (distance, direction)

    def update_state(self, distance: float, direction: Vector2) -> None:
        # Priority 1: Freeze state changes during knockback
        if self.knockback_timer.active:
            return

        # Priority 2: Manage active attack lock
        if self.state == 'attack':
            self.speed = ENTITY_DATA[self.obj_name].get('attack_speed', self.stats['speed'])
            if self.animation_index >= len(self.animation_frames):
                self.attack_cooldown_timer.activate()
                self.animation_index = 0
                self.speed = self.stats['speed']
                self.state = 'move'
            return

        # Priority 3: Transition non-attacking states
        if distance <= self.attack_radius and not self.attack_cooldown_timer.active:
            self.state = 'attack'
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
