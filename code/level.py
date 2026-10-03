"""Functions are sorted according to execution order."""
from menutab import *

class Level:
    def __init__(self, game: Game, map: str) -> None:
        self.game = game
        self.active_dialogue: Optional[DialogueBox] = None
        self.animation_player = AnimationPlayer(game)
        self.player = Player(self.game, Vector2(0,0), self.game.entity_images['player']['down'])
        self.create_map(map, self.game.last_saved_current_map)
        self.create_camera()
        self.set_camera_boundaries()

    def create_map(self, map: str, player_pos: str) -> None:
        self.current_map = map
        self.game.play_music(self.current_map)
        self.sprites: list[Sprite|AnimatedEffect] = []
        self.particle_and_effect_sprites: list[AnimatedEffect] = []
        self.collision_boxes: list[Rectangle] = []
        self.zones: list[Zone] = []
        self.floor_image = self.game.level_images[self.current_map]

        # --- Collision tiles ---
        collision_layer = cast(TiledMap, self.game.maps[self.current_map].get_layer_by_name('collision_tiles'))
        for x,y,_ in collision_layer.tiles():
                self.collision_boxes.append(Rectangle(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # --- Objects ---
        for obj in self.game.maps[self.current_map].objects:
            pos = Vector2(obj.x, obj.y)
            tile_properties = self.game.maps[self.current_map].get_tile_properties_by_gid(obj.gid) or {}

            # visible tiles
            if obj.visible:
                sprite_to_add = None
                match(obj.type):
                    case 'player':
                        if obj.name == player_pos:
                            sprite_to_add = self.player
                            self.player.set_position(Vector2(pos.x, pos.y))
                    case 'enemy':
                        sprite_to_add = Enemy(self.game, obj.name, pos, self.game.entity_images[obj.name]['idle'])
                    case 'tile':
                        obj_name = obj.name.strip('0123456789')
                        obj_variant = int(re.sub(r"[^0-9]", "", obj.name))
                        sprite_to_add = Tile(self.game, obj_name, pos, self.game.tile_images[obj_name][obj_variant])
                        self.collision_boxes.append(sprite_to_add.hitbox)
                    case _:
                        print(obj) # DEBUGGING
                if sprite_to_add: self.sprites.append(sprite_to_add)
                        
            # collision boxes and zones
            elif not obj.visible:
                match(obj.type):
                    case 'collision':
                        self.collision_boxes.append(Rectangle(pos.x, pos.y, obj.width, obj.height))
                    case 'zone':
                        origin_map = self.current_map
                        self.zones.append(Zone(obj.name, obj.properties['shape'], origin_map, pos, obj.width, obj.height))
                    case 'marker':
                        if not 'sword' in self.player.inventory.slot_items:
                            self.sprites.append(CollectibleSword(self.game, obj.name, pos, self.game.slot_item_images[obj.name]))
                   
    def create_camera(self) -> None:
        self.camera = Camera2D()
        self.camera.zoom = CAMERA_ZOOM
        self.camera.target = self.player.center
        self.camera.offset = Vector2(*SCREEN_CENTER)

    def set_camera_boundaries(self) -> None:
        # --- Camera boundaries ---
        map_width = self.game.maps[self.current_map].width * TILE_SIZE
        map_height = self.game.maps[self.current_map].height * TILE_SIZE

        # determine screen center
        half_viewport_width = (SCREEN_WIDTH/self.camera.zoom) / 2
        half_viewport_height = (SCREEN_HEIGHT/self.camera.zoom) / 2

        # set max x and y
        min_x = half_viewport_width
        max_x = map_width - half_viewport_width

        min_y = half_viewport_height
        max_y = map_height - half_viewport_height

        # clamp to middle of the map if it is smaller than the screen
        target_x = map_width / 2 if max_x < min_x else clamp(self.player.center.x, min_x, max_x)
        target_y = map_height / 2 if max_y < min_y else clamp(self.player.center.y, min_y, max_y)

        self.camera_target = Vector2(target_x,target_y)
        self.camera.target = self.camera_target

    def run(self, dt: float) -> None:
        # --- updating ---
        if not self.active_dialogue:
            dt = dt * self.game.debug.game_speed[0]
            if not any((self.game.fade_to_black_timer.active, self.game.fade_from_black_timer.active)):
                self.manage_collisions(dt)
            self.update_sprites(dt)
            self.set_camera_boundaries()

        # --- drawing ---
        begin_texture_mode(self.game.virtual_screen)
        # draw on virtual screen
        clear_background(RAYWHITE)
        begin_mode_2d(self.camera)
        # floor image
        draw_texture(cast(Texture,self.floor_image), 0, 0, WHITE)   
        self.game.debug.draw_grid_2d(10000, 10000, 64, BLACK)   
        self.draw_sprites()
        self.game.debug.draw_hitboxes()
        end_mode_2d()
        end_texture_mode()

    def manage_collisions(self, dt: float) -> None:
        # --- zone collisions ---
        for zone in self.zones:
            player_hit_zone = False
            if isinstance(zone.shape, type(Rectangle())):
                player_hit_zone = check_collision_recs(self.player.hitbox, zone.shape)
            elif isinstance(zone.shape, Circle):
                player_hit_zone = check_collision_circle_rec(zone.shape.center, zone.shape.radius, self.player.hitbox)

            if player_hit_zone:
                self.game.play_sfx('transition')
                self.game.fade_to_black_timer.activate(alternate_callback=lambda: (self.create_map(zone.obj_name, zone.player_pos), self.game.fade_from_black_timer.activate()))
                return

        # --- sprite collisions ---
        for sprite in self.sprites:
            # enemy collides with...
            if isinstance(sprite, Enemy):
                enemy_hit_player = check_collision_recs(sprite.hitbox, self.player.hitbox)
                if enemy_hit_player and not self.player.hurt_timer.active:
                    self.game.play_sfx('player_hurt', PITCH_VARIATION_PLAYER_HURT)
                    self.player.hurt(sprite.damage, vector2_subtract(self.player.center, sprite.center))
                if self.player.weapon:
                    enemy_hit_sword = check_collision_recs(sprite.hitbox, self.player.weapon.hitbox)
                    if enemy_hit_sword and not sprite.hurt_timer.active:
                        self.game.play_sfx('enemy_hurt', PITCH_VARIATION_ENEMY_HURT)
                        sprite.hurt(self.player.damage, vector2_subtract(sprite.center, self.player.center))

            # tile collides with...
            elif isinstance(sprite, Tile):
                if sprite.obj_name == 'grass':
                    if self.player.weapon:
                        tile_hit_sword = check_collision_recs(sprite.hitbox, self.player.weapon.hitbox)
                        if tile_hit_sword:
                            self.game.play_sfx('grass_cut', PITCH_VARIATION_GRASS_CUT)
                            self.sprites.remove(sprite)
                            self.collision_boxes.remove(sprite.hitbox)
                            self.animation_player.create_grass_particles(sprite.center)
                            if self.player.health < self.player.max_health and uniform(0, 1) <= HEART_FROM_GRASS_PROBABILITY:
                                self.sprites.append(HealingHeart(self.game, 'healing_heart', sprite.center, self.game.collectibles_images['healing_heart']))

            # item collides with...
            elif isinstance(sprite, CollectibleItem):
                player_touched_item = check_collision_recs(sprite.hitbox, self.player.hitbox)
                if player_touched_item:
                    sprite.apply_item_effect()
                    self.sprites.remove(sprite)

    def update_sprites(self, dt: float) -> None:
        for sprite in self.sprites:
            sprite.update(dt)
        for sprite in self.particle_and_effect_sprites:
            sprite.update(dt)
        self.camera.target = self.camera_target

    def draw_sprites(self) -> None:
        self.sprites.sort(key=attrgetter('y_sort_pos'))
        for sprite in self.sprites:
            sprite.draw()
        self.particle_and_effect_sprites.sort(key=attrgetter('y_sort_pos'))
        for sprite in self.particle_and_effect_sprites:
            sprite.draw()

    def draw_ui(self) -> None:
        begin_texture_mode(self.game.virtual_screen)

        # --- Player Hearts ---
        remaining_heart_health = self.player.health
        for i in range(0, (int(self.player.max_health) // 4)):
            if remaining_heart_health >= 4:
                heart_texture = 'full_heart'
            elif remaining_heart_health == 3:
                heart_texture = 'three_quarters_heart'
            elif remaining_heart_health == 2:
                heart_texture = 'half_heart'
            elif remaining_heart_health == 1:
                heart_texture = 'quarter_heart'
            else:
                heart_texture = 'empty_heart'
            texture = self.game.ui_images[heart_texture] 
            shaking = 0 if self.player.health > 4 or i > 0 else sin(self.game.play_time * 25) * 2
            draw_texture(texture, int(10 + 36 * (i % 10) + shaking), 10 if i < 10 else 46, WHITE)
            remaining_heart_health -= 4

        # --- Item Slots ---
        # slot 1
        rect_rounding = 0.2
        rect_1 = Rectangle(15, SCREEN_HEIGHT - 135, 70, 120)
        draw_text_ex(self.game.fonts['item_slot_number'], '1', Vector2(rect_1.x + rect_1.width / 2 - 10, rect_1.y - 30), FONT_SIZES['item_slot_number'], 0, COLORS['item_slot_number'])
        draw_rectangle_rounded(rect_1, rect_rounding, 1, COLORS['item_slot_bg'])
        draw_rectangle_rounded_lines_ex(rect_1, rect_rounding, 1, 4, COLORS['item_slot_outline'])
        scale = 1.5 if not self.game.input_pressed('item_slot_1') or self.game.fade_to_black_timer.active or self.game.fade_from_black_timer.active else 1.7
        if self.player.slot_1_item:
            draw_texture_ex(self.game.slot_item_images[self.player.slot_1_item], Vector2(15 + rect_1.width / 2 - self.game.slot_item_images[self.player.slot_1_item].width / 2 * scale, SCREEN_HEIGHT - 135 + rect_1.height/2 - self.game.slot_item_images[self.player.slot_1_item].height /2 * scale), 0, scale, WHITE)
        # slot 2
        rect_2 = Rectangle(110, SCREEN_HEIGHT - 135, 70, 120)
        draw_text_ex(self.game.fonts['item_slot_number'], '2', Vector2(rect_2.x + rect_2.width / 2 - 12, rect_2.y - 30), FONT_SIZES['item_slot_number'], 0, COLORS['item_slot_number'])
        draw_rectangle_rounded(rect_2, rect_rounding, 1, COLORS['item_slot_bg'])
        draw_rectangle_rounded_lines_ex(rect_2, rect_rounding, 1, 4, COLORS['item_slot_outline'])
        scale = 1.5 if not self.game.input_pressed('item_slot_2') or self.game.fade_to_black_timer.active or self.game.fade_from_black_timer.active else 1.7
        if self.player.slot_2_item:
            draw_texture_ex(self.game.slot_item_images[self.player.slot_2_item], Vector2(110 + rect_2.width / 2 - self.game.slot_item_images[self.player.slot_2_item].width / 2 * scale, SCREEN_HEIGHT - 135 + rect_2.height/2 - self.game.slot_item_images[self.player.slot_2_item].height /2 * scale), 0, scale, WHITE)

        # --- Collectibles ---
        draw_texture(self.game.collectibles_images['shell'], SCREEN_WIDTH - 160, 20, BLUE)
        draw_text_ex(self.game.fonts['shell_count'], F" X{self.player.inventory.item_counts['shells']:02d}", Vector2(SCREEN_WIDTH - 118, 32), FONT_SIZES['shell_count'], 0, COLORS['shell_count_shadow'])
        draw_text_ex(self.game.fonts['shell_count'], F" X{self.player.inventory.item_counts['shells']:02d}", Vector2(SCREEN_WIDTH - 120, 30), FONT_SIZES['shell_count'], 0, COLORS['shell_count'])

        if self.active_dialogue: self.active_dialogue.draw()

        end_texture_mode()
