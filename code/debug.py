from utils import *
from enemy import Enemy

class Debug:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.show_debug_infos = ffi.new('bool *', False)
        self.show_hitboxes = ffi.new('bool *', False) 
        self.show_grid_2d = ffi.new('bool *', False) 
        self.game_speed = ffi.new('float *', 1.0)
        self.camera_zoom = ffi.new('float *', 1.0)
        self.show_debug_window = ffi.new('bool *', False)
        self.target_fps = ffi.new('float *', TARGET_FPS)
        self.selected_enemy_id = ffi.new('int *', 0)
        self.enemy_types = ["raccoon", "spirit", "squid", "bamboo"]
        
        self.window_bounds = Rectangle(10, 10, 280, 380)
        self.is_dragging = False
        self.drag_offset = Vector2(0, 0)
        self.info_queue: list[str] = []

    def log_info(self, text: str) -> None:
        """Queue a custom debug string to be displayed in the panel."""
        if self.show_debug_infos[0]:
            self.info_queue.append(text)

    def draw_debug_info_panel(self, pos_x: int = SCREEN_WIDTH - 310, pos_y: int = 10) -> None:
        """Renders debug stats safely across all game states."""
        if not self.show_debug_infos[0]:
            self.info_queue.clear()
            return

        lines: list[str] = []
        
        # --- 1. Global Game Stats ---
        lines.append(f"FPS: {get_fps()}")
        if hasattr(self.game, 'play_time') and hasattr(self.game, 'runtime'):
            lines.append(f"Play time: {self.game.play_time:.1f}s | Total: {self.game.runtime:.1f}s")

        # --- 2. Level-Specific Stats ---
        level = getattr(self.game, 'level', None)
        if level is not None:
            if hasattr(level, 'sprites'):
                lines.append(f"Sprites: {len(level.sprites)}")
        else:
            lines.append(f"State: {self.game.state.capitalize()}")

        # --- 3. Custom Queued Messages ---
        lines.extend(self.info_queue)
        self.info_queue.clear()

        if not lines:
            return

        # --- Layout & Rendering ---
        font = getattr(self.game, 'debugging_font', None) or get_font_default()
        font_size = 18
        line_height = 26
        header_offset = 24
        padding = 12

        max_width = max(measure_text_ex(font, line, font_size, 1).x for line in lines)
        panel_width = max(280, int(max_width) + (padding * 2))
        pos_x = SCREEN_WIDTH - panel_width - 10

        total_height = header_offset + (len(lines) * line_height) + padding
        panel_rec = Rectangle(pos_x, pos_y, panel_width, total_height)

        # Dark background fill + Group Box
        draw_rectangle_rec(panel_rec, Color(15, 15, 20, 225))
        gui_group_box(panel_rec, "Game Info")

        # Render text lines
        for i, line in enumerate(lines):
            text_pos = Vector2(
                panel_rec.x + padding, 
                panel_rec.y + header_offset + (i * line_height)
            )
            draw_text_ex(font, line, text_pos, font_size, 1, WHITE)

    def draw_debug_gui(self) -> None:
        # Toggle developer window with F3
        if is_key_pressed(KEY_F3):
            self.show_debug_window[0] = not self.show_debug_window[0]
            self.show_debug_infos[0] = self.show_debug_window[0]

        if not self.show_debug_window[0] and not self.show_debug_infos[0]:
            return

        begin_texture_mode(self.game.virtual_screen)

        # Render Developer Tools Window if open
        if self.show_debug_window[0]:
            mouse_pos = get_mouse_position()
            
            # Drag & Drop
            title_bar = Rectangle(self.window_bounds.x, self.window_bounds.y, self.window_bounds.width - 24, 24)
            if is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and check_collision_point_rec(mouse_pos, title_bar):
                self.is_dragging = True
                self.drag_offset = Vector2(mouse_pos.x - self.window_bounds.x, mouse_pos.y - self.window_bounds.y)

            if is_mouse_button_released(MOUSE_BUTTON_LEFT):
                self.is_dragging = False

            if self.is_dragging:
                self.window_bounds.x = mouse_pos.x - self.drag_offset.x
                self.window_bounds.y = mouse_pos.y - self.drag_offset.y

            if gui_window_box(self.window_bounds, "Developer Tools (F3)"):
                self.show_debug_window[0] = False

            win_x, win_y = self.window_bounds.x, self.window_bounds.y

            # --- enemy selection button ---
            gui_combo_box(
                Rectangle(win_x + 40, win_y + 30, 200, 25), 
                ";".join(self.enemy_types), 
                self.selected_enemy_id
            )

            # --- enemy spawn button ---
            if gui_button(Rectangle(win_x + 15, win_y + 70, 250, 25), "Spawn Enemy"):
                self.spawn_enemy()

            gui_check_box(Rectangle(win_x + 15, win_y + 110, 20, 20), "Show Hitboxes", self.show_hitboxes)
            gui_check_box(Rectangle(win_x + 15, win_y + 150, 20, 20), "Show Grid 2D", self.show_grid_2d)
            gui_check_box(Rectangle(win_x + 15, win_y + 190, 20, 20), "Show Game Infos", self.show_debug_infos)

            gui_slider(
                Rectangle(win_x + 75, win_y + 220, 130, 20), 
                "Speed: ", 
                f"{self.game_speed[0]:.1f}x", 
                self.game_speed, 
                0.1, 
                3.0
            )

            gui_slider(
                Rectangle(win_x + 75, win_y + 260, 130, 20), 
                "Zoom: ", 
                f"{self.camera_zoom[0]:.1f}x", 
                self.camera_zoom, 
                0.5, 
                5.0
            )
            if hasattr(self.game, 'level') and hasattr(self.game.level, 'camera'):
                self.game.level.camera.zoom = self.camera_zoom[0]

            old_target_fps = self.target_fps[0]
            gui_slider(
                Rectangle(win_x + 75, win_y + 300, 130, 20), 
                "Target FPS: ",
                f"{int(self.target_fps[0])}",
                self.target_fps,
                10,
                240
            )
            if old_target_fps != self.target_fps[0]:
                set_target_fps(int(self.target_fps[0]))

            if hasattr(self.game, 'level') and hasattr(self.game.level, 'player'):
                health_ptr = ffi.new('float *', float(self.game.level.player.health))
                gui_slider(
                    Rectangle(win_x + 75, win_y + 340, 130, 20), 
                    "Health: ", 
                    f"{int(health_ptr[0])}", 
                    health_ptr, 
                    1, 
                    80
                )
                self.game.level.player.health = int(health_ptr[0])

        # Render Info Panel
        if self.show_debug_infos[0]:
            self.draw_debug_info_panel()

        end_texture_mode()

    def draw_hitboxes(self) -> None:
        if self.show_hitboxes[0]:
            for collision_box in self.game.level.collision_boxes:
                draw_rectangle_lines_ex(collision_box, 3, DARKGRAY)        
            for sprite in self.game.level.sprites:
                color = BLUE if sprite.hitbox in self.game.level.collision_boxes else RED if not sprite.obj_name == 'healing_heart' else GREEN
                if sprite.hitbox:
                    draw_rectangle_lines_ex(sprite.hitbox, 3, color)
            for zone in self.game.level.zones:
                if zone.shape_name == 'rectangle':
                    draw_rectangle_lines_ex(cast(Rectangle, zone.shape), 3, PURPLE)
                elif zone.shape_name == 'ellipse':
                    circle = cast(Circle, zone.shape)
                    draw_circle_lines_v(circle.center, circle.radius, PURPLE)

    def draw_grid_2d(self, width: int, height: int, cell_size: int, color: Color = LIGHTGRAY) -> None:
        if self.show_grid_2d[0]:
            for x in range(0, width + 1, cell_size):
                draw_line(x, 0, x, height, color)
            for y in range(0, height + 1, cell_size):
                draw_line(0, y, width, y, color)

    def spawn_enemy(self):
        enemy_name = self.enemy_types[self.selected_enemy_id[0]]
        spawn_pos = vector2_add(self.game.level.player.pos, Vector2(260, 0)) # Spawn right next to player
        self.game.level.sprites.append(
            Enemy(self.game, enemy_name, spawn_pos, self.game.entity_images[enemy_name]['idle'])
        )

    def get_func_time(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time: float = perf_counter()
            result: Any = func(*args, **kwargs)
            end_time: float = perf_counter()
            print(f'"{func.__name__}()" took {end_time - start_time:.3f} seconds to execute')
            return result
        return wrapper

class DummyDebug:
    """No-op debug object for production release builds."""
    game_speed = [1.0]

    def log_info(self, *args, **kwargs) -> None: pass
    def draw_debug_info_panel(self, *args, **kwargs) -> None: pass
    def draw_grid_2d(self, *args, **kwargs) -> None: pass
    def draw_hitboxes(self, *args, **kwargs) -> None: pass
    def draw_debug_gui(self, *args, **kwargs) -> None: pass
