from managers import *

class Game:
    def __init__(self) -> None:
        self.init_raylib()
        self.init_paths()
        self.import_graphics()
        self.import_audio()
        self.import_world_data()
        self.init_managers()
        self.load_settings()
        self.load_save_data()
        set_window_icon(cast(Image, self.ui_images['icon']))

    def run(self) -> None:
        while not window_should_close():
            dt = get_frame_time()
            self.input_manager.get_general_input()
            self.state_manager.change_game_mode()
            self.audio_manager.update()
            self.time_manager.update_play_time()
            self.state_manager.handle_game_mode(dt)
            #debug(self, self.font, f"Play time: {self.time_manager.play_time:.2f} | Total time: {self.time_manager.runtime:.2f}")  # DEBUGGING
            if hasattr(self.state_manager, 'level'): debug(self, self.fonts['regular'], f"Player State: {self.state_manager.level.player.animation_state}")  # DEBUGGING
            if hasattr(self.state_manager, 'level'): debug(self, self.fonts['regular'], f"Player attacking: {self.state_manager.level.player.attacking}", 10, 100)  # DEBUGGING
            self.draw_virtual_screen()

    def title_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        draw_texture(self.background_images['title'], 0, 0, WHITE)
        title_size = measure_text_ex(self.fonts['title'], GAME_NAME, TITLE_FONT_SIZE, TITLE_FONT_SPACING)
        height_animation = 5 * sin(self.time_manager.runtime*3)
        draw_text_ex(self.fonts['title'], GAME_NAME, Vector2(SCREEN_CENTER[0]+5-title_size.x/2,SCREEN_CENTER[1]+height_animation-title_size.y/2), TITLE_FONT_SIZE, TITLE_FONT_SPACING, GREEN)
        draw_text_ex(self.fonts['title'], GAME_NAME, Vector2(SCREEN_CENTER[0]-title_size.x/2,SCREEN_CENTER[1]+5+height_animation-title_size.y/2), TITLE_FONT_SIZE, TITLE_FONT_SPACING, GREEN)
        draw_text_ex(self.fonts['title'], GAME_NAME, Vector2(SCREEN_CENTER[0]-5-title_size.x/2,SCREEN_CENTER[1]+height_animation-title_size.y/2), TITLE_FONT_SIZE, TITLE_FONT_SPACING, GREEN)
        draw_text_ex(self.fonts['title'], GAME_NAME, Vector2(SCREEN_CENTER[0]-title_size.x/2,SCREEN_CENTER[1]-5+height_animation-title_size.y/2), TITLE_FONT_SIZE, TITLE_FONT_SPACING, GREEN)
        draw_text_ex(self.fonts['title'], GAME_NAME, Vector2(SCREEN_CENTER[0]-title_size.x/2,SCREEN_CENTER[1]+height_animation-title_size.y/2), TITLE_FONT_SIZE, TITLE_FONT_SPACING, BLACK)
        end_texture_mode()

    def pause_menu(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        self.state_manager.level.draw_sprites()
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['pause_menu_tint'])
        end_texture_mode()

    def game_over_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        end_texture_mode()

    def draw_virtual_screen(self) -> None:
        begin_drawing()
        clear_background(BLACK)

        # check screen size and scale
        current_screen_width, current_screen_height = get_screen_width(), get_screen_height()
        scale = min(current_screen_width / SCREEN_WIDTH, current_screen_height / SCREEN_HEIGHT)

        # calculate and draw virtual screen
        source_rect = Rectangle(0, 0, SCREEN_WIDTH, -SCREEN_HEIGHT)
        dest_rect = Rectangle((current_screen_width - (SCREEN_WIDTH * scale)) / 2,
                            (current_screen_height - (SCREEN_HEIGHT * scale)) / 2, 
                            SCREEN_WIDTH * scale, 
                            SCREEN_HEIGHT * scale)

        draw_texture_pro(self.virtual_screen.texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)

        end_drawing()

    def save_game_data(self) -> None:
        if not hasattr(self.state_manager, 'level'):
            return
        current_process = 'Saving game data'
        save_data = load_file(self.SAVE_FILE, current_process)

        save_data['current_map'] = self.state_manager.level.current_map

        save_file(self.SAVE_FILE, save_data, current_process)

    def save_runtime(self) -> None:
        current_process = 'Saving runtime'
        save_data = load_file(self.SAVE_FILE, current_process)

        accumulated_time = self.total_runtime if hasattr(self, 'total_runtime') else 0.0
        save_data['total_runtime'] = self.time_manager.runtime + accumulated_time

        save_file(self.SAVE_FILE, save_data, current_process)

# --- Initialization steps ---

    def init_raylib(self) -> None:
        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_NAME)
        init_audio_device()
        set_target_fps(TARGET_FPS)
        self.virtual_screen = load_render_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
        if START_IN_FULLSCREEN: toggle_fullscreen()

    def init_paths(self) -> None:
        # --- detect running mode ---
        if getattr(sys, "frozen", False):
            base_dir = sys._MEIPASS # type: ignore
            user_dir = os.path.expanduser(join('~', 'Documents', GAME_NAME))
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            user_dir = join(base_dir, 'data')
        saves_dir = join(user_dir, 'saves')

        # --- create save directory if needed ---
        os.makedirs(user_dir, exist_ok=True)
        os.makedirs(saves_dir, exist_ok=True)

        # --- asset file paths ---
        self.BASE_DIR = base_dir
        self.USER_DIR = user_dir
        self.GRAPHICS_DIR = join(base_dir, 'graphics')
        self.FONTS_DIR = join(base_dir, 'fonts')
        self.SFX_DIR = join(base_dir, 'audio', 'sfx')
        self.MUSIC_DIR = join(base_dir, 'audio', 'music')
        self.DATA_DIR = join(base_dir, 'data')
        self.SETTINGS_FILE = join(user_dir, 'settings.json')
        self.SAVE_FILE = join(user_dir, 'save.json')
        # --- save files ---
        self.SAVE_FILE = join(saves_dir, 'save.json')
        self.SETTINGS_FILE = join(saves_dir, 'settings.json')

    def import_graphics(self) -> None:
        self.player_images: dict[str, list[Texture]] = {
            'down': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'down')),
            'down_attack': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'down_attack')),
            'down_idle': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'down_idle')),
            'up': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'up')),
            'up_attack': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'up_attack')),
            'up_idle': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'up_idle')),
            'right': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'right')),
            'right_attack': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'right_attack')),
            'right_idle': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'right_idle')),
            'left': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'left')),
            'left_attack': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'left_attack')),
            'left_idle': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', 'left_idle')),
        }
        
        self.ui_images: dict[str, Image] = {
            'icon': load_image(join(self.GRAPHICS_DIR, 'ui', 'icon.png')),      
            }

        self.background_images: dict[str, Texture] = {
            'title': load_texture(join(self.GRAPHICS_DIR, 'ui', 'title_background.png')),
        }

        self.level_images: dict[str, Image | Texture | list[Texture]] = {            
            'start_area': load_texture(join(self.GRAPHICS_DIR, 'levels', 'start_area.png')),
            'cave': load_texture(join(self.GRAPHICS_DIR, 'levels', 'cave.png')),
            'cave2': load_texture(join(self.GRAPHICS_DIR, 'levels', 'cave2.png')),
            }

        self.object_images: dict[str, Image | Texture | list[Texture]] = {
            'column': load_texture(join(self.GRAPHICS_DIR, 'objects', 'column.png')),
            'rocks': import_image_folder(join(self.GRAPHICS_DIR, 'objects', 'rocks')),
            'grass': import_image_folder(join(self.GRAPHICS_DIR, 'objects', 'grass')),
            }

        self.entity_image: dict[str, Image | Texture | list[Texture]] = {

        }

        self.fonts: dict[str, Font] = {
            'title': load_font(join(self.FONTS_DIR, 'slkscr.ttf')),
            'regular': load_font(join(self.FONTS_DIR, 'Pixelbasel.ttf')),
            }

    def import_audio(self) -> None:
        # --- music ---
        self.music: dict[str, Music] = {
            'title': load_music_stream(join(self.MUSIC_DIR, 'title.wav')),
            'start_area': load_music_stream(join(self.MUSIC_DIR, 'start_area.wav')),
            'cave': load_music_stream(join(self.MUSIC_DIR, 'cave.wav')),
        }

        # --- sfx ---
        self.sfx: dict[str, Sound] = {
            'transition': load_sound(join(self.SFX_DIR, 'transition.wav')),
        }

    def import_world_data(self) -> None:
        self.maps: dict[str, TiledMap] = {
            'start_area': TiledMap(join(self.DATA_DIR, 'maps', 'start_area.tmx')),
            'cave': TiledMap(join(self.DATA_DIR, 'maps', 'cave.tmx')),
            'cave2': TiledMap(join(self.DATA_DIR, 'maps', 'cave2.tmx')),
            }

    def init_managers(self) -> None:
        self.state_manager = StateManager(self)
        self.time_manager = TimeManager(self)
        self.input_manager = InputManager(self)
        self.audio_manager = AudioManager(self)

    def load_settings(self) -> None:
        self.input_manager.load_user_bindings()

    def load_save_data(self) -> None:
        save_data = load_file(self.SAVE_FILE)
        self.total_runtime = save_data.get('total_runtime', 0.0)
        self.last_saved_current_map: str = save_data.get('current_map', 'start_area')

if __name__ == '__main__':
    game = Game()
    game.run()
    game.save_runtime()
    game.save_game_data()
    game.input_manager.save_user_bindings()
    # --- Cleanup ---
    close_window()
    close_audio_device()
    sys.exit()
