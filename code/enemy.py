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

    def update(self, dt: float):
        self.set_state()
        super().update(dt)

    def get_player_distance_direction(self) -> tuple[float, Vector2]:
        distance_vector = vector2_subtract(self.game.level.player.center, self.center)
        distance = vector2_length(distance_vector)

        if distance > 0:
            direction = vector2_normalize(distance_vector)
        else:
            direction = Vector2()
        
        return (distance, direction)

    def set_state(self):
        distance = self.get_player_distance_direction()[0]
        if self.state == 'attack' or self.knockback_timer.active:
            return

        if distance <= self.attack_radius and not self.attack_cooldown_timer.active:
            if not self.state == 'attack':
                self.state = 'attack'
                self.animation_index = 0
        elif distance <= self.notice_radius:
            self.state = 'move'
            self.direction = self.get_player_distance_direction()[1]
        else:
            self.state = 'idle'
            self.direction = Vector2()
    
    def attack(self):
        pass

    def update_appearance(self, dt: float):
        # --- Update texture frame ---
        if self.state == 'attack':
            if self.animation_index >= len(cast(list, self.animation_frames)):   
                self.attack_cooldown_timer.activate()
                self.animation_index = 0
                self.state = 'move'
        self.animation_frames = self.game.entity_images[self.obj_name][self.state]
        self.animation_index += ENEMY_ANIMATION_SPEED * self.speed * dt
        super().update_appearance(dt)
