"""Functions are sorted according to execution order."""
from menutab import *

class Level:
    def __init__(self, game: Game, map: str) -> None:
        self.game = game
        self.animation_player = AnimationPlayer(game)
        self.player = Player(self.game, Vector2(0,0), self.game.entity_images['player']['down'])
        self.create_map(map, self.game.last_saved_current_map)
        self.create_camera()
        self.set_camera_boundaries()

    def create_map(self, map: str, player_pos: str) -> None:
        self.current_map = map
        self.game.play_music(self.current_map)
        self.sprites: list[Sprite] = []
        self.particle_sprites: list[ParticleEffect] = []
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
                        sprite_to_add = Tile(self.game, obj.name, pos, self.game.tile_images[obj.name][obj.properties.get('version', tile_properties.get('version', 1))])
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
        self.manage_collisions(dt)
        self.update_sprites(dt)
        self.set_camera_boundaries()

        # --- drawing ---
        begin_texture_mode(self.game.virtual_screen)
        self.draw_sprites()
        end_texture_mode()
        self.draw_ui()

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
                self.create_map(zone.obj_name, zone.player_pos)
                self.set_camera_boundaries()
                return

        # --- sprite collisions ---
        for sprite in self.sprites:
            # enemy collides with...
            if isinstance(sprite, Enemy):
                enemy_hit_player = check_collision_recs(sprite.hitbox, self.player.hitbox)
                if enemy_hit_player and not self.player.hurt_timer.active:
                    self.game.play_sfx('player_hurt', PITCH_VARIATION_PLAYER_HURT)
                    self.player.hurt(sprite.damage, vector2_negate(vector2_normalize(sprite.get_player_distance_direction()[1])))
                if self.player.sword:
                    enemy_hit_sword = check_collision_recs(sprite.hitbox, self.player.sword.hitbox)
                    if enemy_hit_sword and not sprite.hurt_timer.active:
                        self.game.play_sfx('enemy_hurt', PITCH_VARIATION_ENEMY_HURT)
                        sprite.hurt(self.player.damage, vector2_normalize(sprite.get_player_distance_direction()[1]))

            # tile collides with...
            elif isinstance(sprite, Tile):
                if sprite.obj_name == 'grass':
                    if self.player.sword:
                        tile_hit_sword = check_collision_recs(sprite.hitbox, self.player.sword.hitbox)
                        if tile_hit_sword:
                            self.game.play_sfx('grass_cut', PITCH_VARIATION_GRASS_CUT)
                            self.sprites.remove(sprite)
                            self.collision_boxes.remove(sprite.hitbox)
                            self.animation_player.create_grass_particles(sprite.center)

    def update_sprites(self, dt: float) -> None:
        for sprite in self.sprites:
            sprite.update(dt)
        for sprite in self.particle_sprites:
            sprite.update(dt)
        self.camera.target = self.camera_target

    def draw_sprites(self) -> None:
        # draw on virtual screen
        clear_background(RAYWHITE)
        begin_mode_2d(self.camera)

        # floor image
        draw_texture(cast(Texture,self.floor_image), 0, 0, WHITE)

        # y-sort and draw sprites
        self.sprites.sort(key=attrgetter('y_sort_pos'))
        for sprite in self.sprites:
            sprite.draw()
        self.particle_sprites.sort(key=attrgetter('y_sort_pos'))
        for sprite in self.particle_sprites:
            sprite.draw()

        # hitboxes
        # boxes that are only in self.collison_boxes are green
        # boxes that are from visible sprites AND in self.collision_boxes are blue
        # boxes that are only hitboxes from sprites but not in self.collision_boxes are red
        # transition zones are purple

        #for collision_box in self.collision_boxes:
        #    draw_rectangle_lines_ex(collision_box, 3, GREEN)        
        #for sprite in self.sprites:
        #    color = BLUE if sprite.hitbox in self.collision_boxes else RED
        #    if sprite.hitbox:
        #        draw_rectangle_lines_ex(sprite.hitbox, 3, color)
        #for zone in self.zones:
        #    if zone.shape_name == 'rectangle':
        #        draw_rectangle_lines_ex(cast(Rectangle,zone.shape), 3, PURPLE)
        #    elif zone.shape_name == 'ellipse':
        #        circle = cast(Circle, zone.shape)
        #        draw_circle_lines_v(circle.center, circle.radius, PURPLE)

        end_mode_2d()

    def draw_ui(self) -> None:
        pass
