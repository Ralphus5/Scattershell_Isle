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
        # animation
        self.animation_frames = textures
        self.animation_index: float = 0.0
        # stats
        self.stats = ENTITY_DATA[obj_name]
        self.speed = self.stats['speed']
        self.damage = cast(int, self.stats['damage'])
        self.half_hitbox_offset_vertical = self.stats['hitbox_offset_v'] / 2
        self.half_hitbox_offset_horizontal = self.stats['hitbox_offset_h'] / 2
        self.hitbox = inflate_rect(Rectangle(self.pos.x + self.half_hitbox_offset_horizontal, self.pos.y + self.half_hitbox_offset_vertical, self.texture.width, self.texture.height), -self.stats['hitbox_offset_h'], -self.stats['hitbox_offset_v'])
        self.attack_cooldown = ENTITY_DATA[self.obj_name]['attack_cooldown']
        self.hurt_time = HURT_TIMES[self.__class__.__name__]
        self.knockback_time = KNOCKBACK_TIMES[self.__class__.__name__]
        self.knockback_speed = ENTITY_DATA[self.obj_name]['knockback_speed']
        self.knockback = ENTITY_DATA[self.obj_name]['knockback']
        self.direction = Vector2()

        # timers
        self.timers: list[Timer] = []
        self.hurt_timer = Timer(self.game, self.hurt_time, True, False, False)
        self.knockback_timer = Timer(self.game, self.knockback_time, True, False, False, callback=lambda: setattr(self, 'speed', ENTITY_DATA[self.obj_name]['speed']))
        self.attack_cooldown_timer = Timer(self.game, self.attack_cooldown, True, False, False)
        self.timers.append(self.hurt_timer)
        self.timers.append(self.knockback_timer)
        self.timers.append(self.attack_cooldown_timer)

    def set_position(self, pos: Vector2|tuple[float, float]) -> None:
        self.pos = Vector2(pos[0], pos[1]) if isinstance(pos, tuple) else pos
        self.hitbox.x = self.pos.x + self.half_hitbox_offset_horizontal
        self.hitbox.y = self.pos.y + self.half_hitbox_offset_vertical

    def update(self, dt: float) -> None:
        self.attack()
        self.move(dt)
        self.update_appearance(dt)
        for timer in self.timers:
            timer.update(dt)
            
    def draw(self) -> None:
        if self.hurt_timer.active:
            draw_texture_ex(self.texture, self.pos, 0, 1, Color(255, 255, 255, max(20, int(sin(self.game.play_time * HURT_FLICKER_FREQUENCY) % 255))))
        else:
            draw_texture_ex(self.texture, self.pos, 0, 1, WHITE)

    def check_death(self) -> None:
        if self.health <= 0:
            self.health = 0
            self.game.level.sprites.remove(self)
            self.game.level.animation_player.create_death_animation(self.obj_name, self.center)
            if self.obj_name == 'player':
                self.game.pause_music()
                self.game.play_sfx('game_over')
                self.game.swipe_to_black_timer.activate(DEATH_SWITPE_TO_BLACK_DURATION)
                if self.game.level.player.weapon and self.game.level.player.weapon in self.game.level.sprites:
                    self.game.level.sprites.remove(self.game.level.player.weapon)
                    self.game.level.player.weapon = None
                self.game.requested_state = 'game_over'

    def hurt(self, damage: int, knock_back_directon: Vector2) -> None:
        if not self.hurt_timer.active:
            self.health -= damage
            self.check_death()
            self.hurt_timer.activate()
            self.knockback_timer.activate()
            self.speed = self.knockback_speed * self.knockback
            self.direction = vector2_normalize(knock_back_directon) if vector2_length(knock_back_directon) > 0 else Vector2()

    def attack(self) -> None:
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

        # Hitbox belegt nur die unteren X% des Sprites
        hitbox_h = self.texture.height * hitbox_height_ratio
        hitbox_y = self.pos.y + (self.texture.height - hitbox_h)
        
        self.hitbox = inflate_rect(Rectangle(self.pos.x, hitbox_y, self.texture.width, hitbox_h), 0, -self.texture.height/5)

class SlotItem(Sprite):
    def __init__(self, game: Game, obj_name: str) -> None:
        super().__init__(game, obj_name, Vector2(0,0), game.sword_images[game.level.player.facing_direction])
        self.player = game.level.player
        self.align_to_player()

    def align_to_player(self) -> None:
        direction = self.player.facing_direction
        self.texture = self.game.sword_images[direction]
        p_pos, p_tex = self.player.pos, self.player.texture

        match direction:
            case 'down':  pos = Vector2(p_pos.x + p_tex.width * 0.5, p_pos.y + p_tex.height)
            case 'up':    pos = Vector2(p_pos.x + p_tex.width / 8, p_pos.y - self.texture.height)
            case 'right': pos = Vector2(p_pos.x + p_tex.width, self.player.center.y + 4)
            case 'left':  pos = Vector2(p_pos.x - self.texture.width, self.player.center.y + 4)

        self.pos = pos
        self.hitbox = Rectangle(self.pos.x, self.pos.y, self.texture.width, self.texture.height)
        
    def update(self, dt: float) -> None:
        self.align_to_player()

class Sword(SlotItem):
    def __init__(self, game: Game) -> None:
        super().__init__(game, 'sword')
        self.game.play_sfx(self.obj_name, PITCH_VARIATION_SWORD)

class CollectibleItem(Sprite):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, texture: Texture) -> None:
        super().__init__(game, obj_name, pos, texture)
        self.set_position(vector2_add(self.pos, vector2_subtract(self.pos, self.center)))

    def apply_item_effect(self) -> None:
        pass

class HealingHeart(CollectibleItem):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, texture: Texture) -> None:
        super().__init__(game, obj_name, pos, texture)

    def apply_item_effect(self) -> None:
        self.game.play_sfx('heart_collect')
        self.game.level.player.health += 4
        if self.game.level.player.health >= self.game.level.player.max_health:
            self.game.level.player.health = self.game.level.player.max_health

class Shell(CollectibleItem):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, texture: Texture) -> None:
        super().__init__(game, obj_name, pos, texture)

    def apply_item_effect(self) -> None:
        self.game.play_sfx('shell_collect')
        self.game.level.player.inventory.item_counts['shells'] += 1

class CollectibleSword(CollectibleItem):
    def __init__(self, game: Game, obj_name: str, pos: Vector2, texture: Texture) -> None:
        super().__init__(game, obj_name, pos, texture)

    def apply_item_effect(self) -> None:
        self.game.level.player.inventory.slot_items.add('sword')
        self.game.play_sfx('sword_jingle')
        
        messages = [
            "You obtained the Sword!",
            F"Press '{BUTTON_TO_NAME[CONTROLLER_BINDINGS['open_inventory']] if is_gamepad_available(0) else KEY_TO_NAME[DEFAULT_KEYBOARD_BINDINGS['open_inventory']]}' to open\nthe inventory and equip it to an item slot!",
            "When equipped, press the item slot button\nto use it!"
        ]
        self.game.level.active_dialogue = DialogueBox(self.game, messages)

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
        animation_frames = choice(self.game.particles_images['leaf'])
        assert isinstance(animation_frames, list)
        flip_x = uniform(0, 1) >= 0.5
        particle = AnimatedEffect(self.game, GRASS_PARTICLES_ANIMATION_SPEED, self.game.level.particle_and_effect_sprites, 'leaf', pos, cast(list[Texture], animation_frames), flip_x)
        particle.set_position(Vector2(particle.pos.x, particle.pos.y - GRASS_PARTICLE_OFFSET))

    def create_attack_animation(self, animation_type: str, pos: Vector2|tuple[float, float]) -> None:
        animation_frames = self.game.attack_animations_images[animation_type]
        AnimatedEffect(self.game, ATTACK_ANIMATION_SPEED, self.game.level.particle_and_effect_sprites, animation_type, pos, cast(list[Texture], animation_frames))

    def create_death_animation(self, animation_type: str, pos: Vector2|tuple[float, float]) -> None:
        animation_frames = self.game.death_animations_images[animation_type]
        AnimatedEffect(self.game, DEATH_ANIMATION_SPEED, self.game.level.sprites, animation_type, pos, animation_frames, is_death_anim=True)

class AnimatedEffect(Sprite):
    def __init__(self, game: Game, animation_speed: float, group: list[AnimatedEffect|Sprite]|list[AnimatedEffect], obj_name: str, pos: Vector2|tuple[float, float], textures: list[Texture], flip_x: bool = False, is_death_anim: bool = False) -> None:
        super().__init__(game, obj_name, Vector2(pos[0], pos[1]) if isinstance(pos, tuple) else pos, textures[0])
        self.animation_speed = animation_speed
        self.group = group
        self.group.append(self)
        self.pos = vector2_subtract(self.pos, Vector2(abs(self.texture.width)/2, abs(self.texture.height)/2))
        self.animation_frames = textures
        self.animation_index: float = 0.0
        self.flip_x = flip_x
        self.is_death_anim = is_death_anim

    def draw(self) -> None:
        w, h = self.texture.width, self.texture.height
        source = Rectangle(0, 0, -w if self.flip_x else w, h)
        dest = Rectangle(self.pos.x, self.pos.y, w, h)
        draw_texture_pro(self.texture, source, dest, Vector2(0, 0), 0, WHITE)

    def update(self, dt: float) -> None:
        self.animation_index += self.animation_speed * dt
        if self.animation_index >= len(self.animation_frames):
            self.group.remove(self)
            if self.obj_name in ['raccoon', 'spirit', 'bamboo', 'squid'] and self.is_death_anim:
                if uniform(0, 1) <= SHELL_FROM_ENEMY_PROBABILITY:
                    self.game.level.sprites.append(Shell(self.game, 'shell', self.center, self.game.collectibles_images['shell']))
        else:
            self.texture = self.animation_frames[int(self.animation_index)]
