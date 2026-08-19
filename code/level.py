from player import *

class Level:
    def __init__(self, game: Game, map: str) -> None:
        self.game = game
        self.player = Player(self.game, Vector2(0,0), self.game.player_images['down'])
        self.create_map(map, self.game.last_saved_current_map)
        self.create_camera()
        self.set_camera_boundaries()

    def create_map(self, map: str, player_pos: str) -> None:
        self.current_map = map
        self.game.audio_manager.play_music(self.current_map)
        self.sprites: list[Sprite] = []
        self.collision_boxes: list[Rectangle] = []
        self.zones: list[Zone] = []
        self.sprites.append(self.player)
        self.floor_image = self.game.level_images[self.current_map]

        # --- Collision tiles ---
        collision_layer = cast(TiledMap, self.game.maps[self.current_map].get_layer_by_name('collision_tiles'))
        for x,y,_ in collision_layer.tiles():
                self.collision_boxes.append(Rectangle(x * TILE_SIZE,y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # --- Objects ---
        for obj in self.game.maps[self.current_map].objects:
            pos = Vector2(obj.x, obj.y)

            # visible tiles
            if obj.visible:
                match(obj.type):
                    case 'player':
                        if obj.name == player_pos:
                            self.player.set_position(Vector2(pos.x, pos.y))
                    case 'column':
                        tile = Tile(pos, self.game.object_images[obj.name], 0.5)
                        self.sprites.append(tile)
                        self.collision_boxes.append(tile.hitbox)
                    case 'rock':
                        tile = Tile(pos, self.game.object_images['rocks'][obj.rock_id])
                        self.sprites.append(tile)
                        self.collision_boxes.append(tile.hitbox)
                    case 'grass':
                        tile = Tile(pos, self.game.object_images['grass'][obj.grass_id])
                        self.sprites.append(tile)
                        self.collision_boxes.append(tile.hitbox)
            # collision boxes and zones
            elif not obj.visible:
                match(obj.type):
                    case 'collision':
                        self.collision_boxes.append(Rectangle(pos.x,pos.y,obj.width,obj.height))
                    case 'zone':
                        origin_map = self.current_map
                        if obj.properties['shape'] == 'rectangle':
                            shape = Rectangle(pos.x,pos.y,obj.width,obj.height)
                        elif obj.properties['shape'] == 'ellipse':
                            shape = Circle(Vector2(pos.x + obj.width/2, pos.y + obj.height/2), obj.width/2)
                        self.zones.append(Zone(shape, obj.name, origin_map, obj.properties['shape']))
                   
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
        # --- zone transition ---
        for zone in self.zones:
            collided = False

            if zone.shape_type == 'rectangle':
                collided = check_collision_recs(self.player.hitbox, cast(Rectangle,zone.shape))
            elif zone.shape_type == 'ellipse':
                circle = cast(Circle, zone.shape)
                collided = check_collision_circle_rec(circle.center, circle.radius, self.player.hitbox)

            if collided:
                self.game.audio_manager.play_sfx('transition')
                self.create_map(zone.name, zone.player_pos)
                self.set_camera_boundaries()
                return

        # --- updating ---
        self.update_sprites(dt)
        self.set_camera_boundaries()

        # --- drawing ---
        begin_texture_mode(self.game.virtual_screen)
        self.draw_sprites()
        end_texture_mode()
        self.draw_ui()

    def update_sprites(self, dt: float) -> None:
        for sprite in self.sprites:
            sprite.update(dt)
        self.camera.target = self.camera_target

    def draw_sprites(self) -> None:
        # draw on virtual screen
        clear_background(RAYWHITE)
        begin_mode_2d(self.camera)

        # floor image
        draw_texture(cast(Texture,self.floor_image), 0, 0, WHITE)

        # y-sort and draw sprites
        self.sprites.sort(key=lambda sprite: sprite.y_sort_pos)
        for sprite in self.sprites:
            sprite.draw()

        # hitboxes
        draw_rectangle_lines_ex(self.player.hitbox, 3, BLUE)
        for collision_box in self.collision_boxes:
            draw_rectangle_lines_ex(collision_box, 3, RED)
        for zone in self.zones:
            if zone.shape_type == 'rectangle':
                draw_rectangle_lines_ex(cast(Rectangle,zone.shape), 3, PURPLE)
            elif zone.shape_type == 'ellipse':
                circle = cast(Circle, zone.shape)
                draw_circle_lines_v(circle.center, circle.radius, PURPLE)

        end_mode_2d()

    def draw_ui(self) -> None:
        pass
