"""Functions are sorted according to execution order."""
from utils import *

class Sprite:
    def __init__(self, game: Game, obj_name: str, pos: Vector2, texture: Texture) -> None:
        self.game = game
        self.obj_name = obj_name
        self.pos = pos
        self.texture = texture
        self.hitbox = Rectangle(self.pos.x, self.pos.y, self.texture.width, self.texture.height)

    @property
    def y_sort_pos(self) -> float:
        return self.pos.y + self.texture.height

    @property
    def center(self) -> Vector2:
        return Vector2(self.pos.x + self.texture.width/2, self.pos.y + self.texture.height/2)

    def update(self, dt: float) -> None:
        pass

    def draw(self):
        draw_texture_ex(self.texture, self.pos, 0, 1, WHITE)

    def set_position(self, pos: Vector2|tuple[float, float]) -> None:
        self.pos = Vector2(pos[0], pos[1]) if isinstance(pos, tuple) else pos
        self.hitbox.x = self.pos.x
        self.hitbox.y = self.pos.y

class Entity(Sprite):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, textures: list[Texture]) -> None:
        super().__init__(game, obj_name, pos, textures[0])
        self.animation_frames = textures
        self.animation_index: float = 0.0
        self.timers: list[Timer] = []
        self.hurt_timer = Timer(self.game, HURT_TIMES[self.__class__.__name__], True, False, False)
        self.knockback_timer = Timer(self.game, KNOCKBACK_TIMES[self.__class__.__name__], True, False, False)
        self.attack_cooldown_timer = Timer(self.game, ENTITY_DATA[self.obj_name]['attack_cooldown'], True, False, False)
        self.timers.append(self.hurt_timer)
        self.timers.append(self.knockback_timer)
        self.timers.append(self.attack_cooldown_timer)
        self.direction = Vector2()
        self.speed = 0
        self.health = 0
        self.half_hitbox_offset_vertical = ENTITY_DATA[self.obj_name]['hitbox_offset_v'] / 2
        self.half_hitbox_offset_horizontal = ENTITY_DATA[self.obj_name]['hitbox_offset_h'] / 2
        self.hitbox = inflate_rect(Rectangle(self.pos.x + self.half_hitbox_offset_horizontal, self.pos.y + self.half_hitbox_offset_vertical, self.texture.width, self.texture.height), -ENTITY_DATA[self.obj_name]['hitbox_offset_h'], -ENTITY_DATA[self.obj_name]['hitbox_offset_v'])

    def set_position(self, pos: Vector2|tuple[float, float]) -> None:
        self.pos = Vector2(pos[0], pos[1]) if isinstance(pos, tuple) else pos
        self.hitbox.x = self.pos.x + self.half_hitbox_offset_horizontal
        self.hitbox.y = self.pos.y + self.half_hitbox_offset_vertical

    def update(self, dt: float) -> None:
        self.attack()
        self.move(dt)
        self.update_appearance(dt)
        for timer in self.timers:
            timer.update()
            
    def draw(self):
        if self.hurt_timer.active:
            draw_texture_ex(self.texture, self.pos, 0, 1, Color(255, 255, 255, max(20, int(sin(self.game.play_time * HURT_FLICKER_FREQUENCY) % 255))))
        else:
            draw_texture_ex(self.texture, self.pos, 0, 1, WHITE)

    def check_death(self):
        if self.health <= 0:
            if self.obj_name == 'player':
                self.game.requested_state = 'game_over'
            self.game.level.sprites.remove(self)
            self.game.level.animation_player.create_particles(f"{self.obj_name}_death", self.center)

    def hurt(self, damage: int, knock_back_directon: Vector2) -> None:
        if not self.hurt_timer.active:
            self.speed = ENTITY_DATA[self.obj_name]['speed']
            self.health -= damage
            self.check_death()
            self.hurt_timer.activate()
            self.knockback_timer.activate()
            self.direction = vector2_multiply_value(knock_back_directon, -ENTITY_DATA[self.obj_name]['knockback'])

    def attack(self):
        pass
   
    def move(self, dt: float) -> None:
        if self.attack_cooldown_timer.active and not self.knockback_timer.active:
            return

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
        self.texture = self.animation_frames[int(self.animation_index) % len(self.animation_frames)]

class Tile(Sprite):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, texture: Texture) -> None:
        super().__init__(game, obj_name, pos, texture)

        hitbox_height_ratio = 0.51 if obj_name == 'column' else 0.91
        hitbox_inflation = -10

        # Hitbox belegt nur die unteren X% des Sprites
        hitbox_h = self.texture.height * hitbox_height_ratio
        hitbox_y = self.pos.y + (self.texture.height - hitbox_h)
        
        self.hitbox = inflate_rect(Rectangle(self.pos.x, hitbox_y, self.texture.width, hitbox_h), 0, -self.texture.height/5)

class Sword(Sprite):
    def __init__(self, game: Game, obj_name: str) -> None:
        super().__init__(game, obj_name, Vector2(0,0), game.sword_images[game.level.player.facing_direction])
        self.player = game.level.player
        self.align_to_player()
        self.game.play_sfx(self.obj_name, PITCH_VARIATION_SWORD)

    def align_to_player(self) -> None:
        direction = self.player.facing_direction
        self.texture = self.game.sword_images[direction]
        p_pos, p_tex = self.player.pos, self.player.texture

        match direction:
            case 'down':  pos = Vector2(p_pos.x + p_tex.width / 8, p_pos.y + p_tex.height)
            case 'up':    pos = Vector2(p_pos.x + p_tex.width / 8, p_pos.y - self.texture.height)
            case 'right': pos = Vector2(p_pos.x + p_tex.width, self.player.center.y)
            case 'left':  pos = Vector2(p_pos.x - self.texture.width, self.player.center.y)

        self.pos = pos
        self.hitbox = Rectangle(self.pos.x, self.pos.y, self.texture.width, self.texture.height)
        
    def update(self, dt: float) -> None:
        self.align_to_player()

class Zone():
    def __init__(self, obj_name: str, shape_name: str, player_pos: str, pos: Vector2, width: int, height: int) -> None:
        self.obj_name = obj_name
        self.shape_name = shape_name
        self.player_pos = player_pos

        if self.shape_name == 'rectangle':
            self.shape = Rectangle(pos.x, pos.y, width, height)
        elif self.shape_name == 'ellipse':
            self.shape = Circle(Vector2(pos.x + width/2, pos.y + height/2), width/2)

class AnimationPlayer:
    def __init__(self, game: Game) -> None:
        self.game = game

    def create_grass_particles(self, pos: Vector2|tuple[float, float]) -> None:
        animation_frames = choice(self.game.particle_images['leaf'])
        assert isinstance(animation_frames, list)
        flip_x = uniform(0, 1) >= 0.5
        particle = ParticleEffect(self.game, 'leaf', pos, cast(list[Texture], animation_frames), flip_x)
        particle.set_position(Vector2(particle.pos.x, particle.pos.y - GRASS_PARTICLE_OFFSET))
        self.game.level.particle_sprites.append(particle)

    def create_particles(self, animation_type: str, pos: Vector2|tuple[float, float]) -> None:
        animation_frames = self.game.particle_images[animation_type]
        self.game.level.particle_sprites.append(ParticleEffect(self.game, animation_type, pos, cast(list[Texture], animation_frames)))

class ParticleEffect(Sprite):
    def __init__(self, game: Game, obj_name: str, pos: Vector2|tuple[float, float], textures: list[Texture], flip_x: bool = False) -> None:
        super().__init__(game, obj_name, Vector2(pos[0], pos[1]) if isinstance(pos, tuple) else pos, textures[0])
        self.pos = vector2_subtract(self.pos, Vector2(abs(self.texture.width)/2, abs(self.texture.height)/2))
        self.animation_frames = textures
        self.animation_index: float = 0.0
        self.flip_x = flip_x

    def draw(self) -> None:
        w, h = self.texture.width, self.texture.height
        source = Rectangle(0, 0, -w if self.flip_x else w, h)
        dest = Rectangle(self.pos.x, self.pos.y, w, h)
        draw_texture_pro(self.texture, source, dest, Vector2(0, 0), 0, WHITE)

    def update(self, dt: float) -> None:
        self.animation_index += PARTICLES_ANIMATION_SPEED * dt
        if self.animation_index >= len(self.animation_frames):
            self.game.level.particle_sprites.remove(self)
        else:
            self.texture = self.animation_frames[int(self.animation_index)]
