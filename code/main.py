from level import *

class Game:
    def __init__(self) -> None:
        self.init_raylib()
        self.init_paths()
        self.import_graphics()
        self.import_audio()
        self.import_world_data()
        self.init_state()
        self.load_settings()
        self.load_save_data()
        set_window_icon(cast(Image, self.ui_images['icon']))

# --- GAME LOOP ---
    def run(self) -> None:
        while not window_should_close():
            dt = get_frame_time()
            self.get_general_input()
            self.change_game_mode()
            if self.current_track: update_music_stream(self.current_track)
            self.update_play_time()
            self.handle_game_mode(dt)
            debug(self, self.fonts['regular'], f"Play time: {self.play_time:.2f} | Total time: {self.runtime:.2f}", SCREEN_WIDTH - 400)  # DEBUGGING
            if hasattr(self, 'level'): 
                debug(self, self.fonts['regular'], f"Player State: {self.level.player.animation_state}")  # DEBUGGING
                debug(self, self.fonts['regular'], f"Player attacking: {self.level.player.attacking}", 10, 100)  # DEBUGGING
                debug(self, self.fonts['regular'], f"Sprites : {len(self.level.sprites)}", 10, 200)  # DEBUGGING
                debug(self, self.fonts['regular'], f"Health : {self.level.player.health}", SCREEN_WIDTH - 200, 100)  # DEBUGGING
            self.draw_virtual_screen()

    def change_game_mode(self) -> None:
        if not self.requested_state or self.requested_state == self.state:
            return
        # --- Change state ---
        old, new = self.state, self.requested_state
        self.requested_state = ''
        self.state = new

        # --- Drain input buffer after menu switching ---
        self.input_cooldown_timer.activate()

        # --- TITLE ---
        if new == 'title':
            if old == 'boot':
                self.play_music('title')

        # --- PLAY ---
        elif new == 'play':
            if old == 'title':
                self.level = Level(self, self.last_saved_current_map)
                # set player position if saved
                self.play_start = get_time()
            elif old == 'pause':
                self.resume_play_time()
                self.resume_music()
            elif old == 'game_over':
                self.resume_play_time()
                self.save_game_data()
                self.load_save_data()
                self.level = Level(self, self.last_saved_current_map)
                self.play_music(self.level.current_map, True)

        # --- PAUSE ---
        elif new == 'pause':
            if old == 'play':
                self.pause_play_time()
                self.pause_music()

        # --- GAME OVER ---
        elif new == 'game_over':
            self.pause_music()
            self.pause_play_time()

    def handle_game_mode(self, dt) -> None:
        if self.state == 'title':
            self.title_screen()
        elif self.state == 'play':
            self.level.run(dt)
        elif self.state == 'pause':
            self.pause_menu()
        elif self.state == 'game_over':
            self.game_over_screen()

    def title_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        draw_texture(self.background_images['title'], 0, 0, WHITE)
        title_size = measure_text_ex(self.fonts['title'], GAME_NAME, TITLE_FONT_SIZE, TITLE_FONT_SPACING)
        height_animation = 5 * sin(self.runtime*3)
        draw_text_ex(self.fonts['title'], GAME_NAME, Vector2(SCREEN_CENTER[0]-title_size.x/2,SCREEN_CENTER[1]+5+height_animation-title_size.y/2), TITLE_FONT_SIZE, TITLE_FONT_SPACING, COLORS['title_text_shadow'])
        draw_text_ex(self.fonts['title'], GAME_NAME, Vector2(SCREEN_CENTER[0]-title_size.x/2,SCREEN_CENTER[1]+height_animation-title_size.y/2), TITLE_FONT_SIZE, TITLE_FONT_SPACING, COLORS['title_text'])
        end_texture_mode()

    def pause_menu(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        self.level.draw_sprites()
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
        if not hasattr(self, 'level'):
            return
        current_process = 'Saving game data'
        save_data = load_file(self.SAVE_FILE, current_process)

        save_data['current_map'] = self.level.current_map

        save_file(self.SAVE_FILE, save_data, current_process)

    def save_runtime(self) -> None:
        current_process = 'Saving runtime'
        save_data = load_file(self.SAVE_FILE, current_process)

        accumulated_time = self.total_runtime if hasattr(self, 'total_runtime') else 0.0
        save_data['total_runtime'] = self.runtime + accumulated_time

        save_file(self.SAVE_FILE, save_data, current_process)

# --- INITIALIZATION STEPS ---
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
        self.sword_images: dict[str, Texture] = {
            'down': load_texture(join(self.GRAPHICS_DIR, 'sword', 'down.png')),
            'up': load_texture(join(self.GRAPHICS_DIR, 'sword', 'up.png')),
            'right': load_texture(join(self.GRAPHICS_DIR, 'sword', 'right.png')),
            'left': load_texture(join(self.GRAPHICS_DIR, 'sword', 'left.png')),
        }
        
        self.ui_images: dict[str, Image|Texture] = {
            'icon': load_image(join(self.GRAPHICS_DIR, 'ui', 'icon.png')),  
            'sword': load_texture(join(self.GRAPHICS_DIR, 'sword', 'full.png')),  
            }

        self.background_images: dict[str, Texture] = {
            'title': load_texture(join(self.GRAPHICS_DIR, 'ui', 'title_background.png')),
        }

        self.level_images: dict[str, Image | Texture | list[Texture]] = {
            'start_area': load_texture(join(self.GRAPHICS_DIR, 'levels', 'start_area.png')),
            'cave': load_texture(join(self.GRAPHICS_DIR, 'levels', 'cave.png')),
            'cave2': load_texture(join(self.GRAPHICS_DIR, 'levels', 'cave2.png')),
            }

        self.tile_images: dict[str, list[Texture]] = {
            'column': import_image_folder(join(self.GRAPHICS_DIR, 'tiles', 'column')),
            'rock': import_image_folder(join(self.GRAPHICS_DIR, 'tiles', 'rock')),
            'grass': import_image_folder(join(self.GRAPHICS_DIR, 'tiles', 'grass')),
            }

        self.entity_images: dict[str, dict[str, list[Texture]]] = {
            'player': {f'{direction}{suffix}': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', f'{direction}{suffix}'))
                for direction in ['down', 'right', 'left', 'up']
                for suffix in ['', '_attack', '_idle']},
            'bamboo': {f'{state}': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'monsters', 'bamboo', f'{state}')) for state in ['move', 'idle', 'attack']},
            'spirit': {f'{state}': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'monsters', 'spirit', f'{state}')) for state in ['move', 'idle', 'attack']},
            'squid': {f'{state}': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'monsters', 'squid', f'{state}')) for state in ['move', 'idle', 'attack']},
            'raccoon': {f'{state}': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'monsters', 'raccoon', f'{state}')) for state in ['move', 'idle', 'attack']},
        }

        self.fonts: dict[str, Font] = {
            'title': load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), TITLE_FONT_SIZE, ffi.NULL, 0),
            'regular': load_font_ex(join(self.FONTS_DIR, 'Pixelbasel.ttf'), REGULAR_FONT_SIZE, ffi.NULL, 0),
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
            'sword': load_sound(join(self.SFX_DIR, 'sword.wav')),
            'grass_cut': load_sound(join(self.SFX_DIR, 'grass_cut.wav')),
            'enemy_hurt': load_sound(join(self.SFX_DIR, 'enemy_hurt.wav')),
            'player_hurt': load_sound(join(self.SFX_DIR, 'player_hurt.wav')),
        }

    def import_world_data(self) -> None:
        self.maps: dict[str, TiledMap] = {
            'start_area': TiledMap(join(self.DATA_DIR, 'maps', 'start_area.tmx')),
            'cave': TiledMap(join(self.DATA_DIR, 'maps', 'cave.tmx')),
            'cave2': TiledMap(join(self.DATA_DIR, 'maps', 'cave2.tmx')),
            }

    def init_state(self) -> None:
        # state
        self.state = 'boot'
        self.requested_state = 'title'
        # time
        self.play_time = 0.0
        self.play_start = 0.0
        self.pause_start = 0.0
        self.total_paused = 0.0
        # input
        set_exit_key(0)
        self.input_cooldown_timer = Timer(self, INPUT_COOLDOWN_AFTER_SWITCHING_GAME_MODE, False, False, False)
        self.keyboard_bindings = dict(DEFAULT_KEYBOARD_BINDINGS)
        self.controller_bindings = dict(DEFAULT_CONTROLLER_BINDINGS)
        # audio
        self.set_volumes()
        self.current_key: Optional[str] = None
        self.current_track: Music = self.music['title']

    def load_settings(self) -> None:
        self.load_user_bindings()

    def load_save_data(self) -> None:
        save_data = load_file(self.SAVE_FILE)
        self.total_runtime = save_data.get('total_runtime', 0.0)
        self.last_saved_current_map: str = save_data.get('current_map', 'start_area')

    # --- Input System ---
    def get_general_input(self) -> None:
        self.input_cooldown_timer.update()
        # --- Universal Input ---
        if self.input_pressed('fullscreen'):
            toggle_fullscreen()
            hide_cursor() if is_window_fullscreen() else show_cursor()

        # --- TITLE ---
        if self.state == 'title':
            if self.input_pressed('pause') or self.input_pressed('confirm'):
                self.requested_state = 'play'

        # --- PLAY ---
        elif self.state == 'play':
            if self.input_pressed('pause'):
                self.requested_state = 'pause'

        # --- PAUSE ---
        elif self.state == 'pause':
            if self.input_pressed('pause'):
                self.requested_state = 'play'

        # --- GAME OVER ---
        elif self.state == 'game_over':
            if self.input_pressed('confirm'):
                self.requested_state = 'play'

    def load_user_bindings(self):
        data = load_file(self.SETTINGS_FILE, "Loading keybindings")
        if 'keybindings' in data:
            if 'keyboard' in data['keybindings']:
                self.keyboard_bindings.update(data['keybindings']['keyboard'])
            if 'controller' in data['keybindings']:
                self.controller_bindings.update(data['keybindings']['controller'])

    def save_user_bindings(self):
        current_process = "Saving keybindings"
        save_data = load_file(self.SETTINGS_FILE, current_process)

        current_kb = {k: v for k, v in self.keyboard_bindings.items() if k not in NON_REMAPPABLE_ACTIONS}
        current_ctrl = {k: v for k, v in self.controller_bindings.items() if k not in NON_REMAPPABLE_ACTIONS}

        save_data['keybindings'] = {
                    'keyboard': current_kb,
                    'controller': current_ctrl
                }

        save_file(self.SETTINGS_FILE, save_data, current_process)

    def check_joystick_dead_zone(self, axis: float) -> int:
        if not abs(axis) > CONTROLLER_DEAD_ZONE:
            return 0
        if axis > 0:
            return 1
        else:
            return -1

    def get_player_movement_input(self) -> Vector2:
        direction_x = int(self.input_down('move_right')) - int(self.input_down('move_left'))
        direction_y = int(self.input_down('move_down')) - int(self.input_down('move_up'))

        # stick
        if is_gamepad_available(0):
            stick_x = self.check_joystick_dead_zone(get_gamepad_axis_movement(0, GAMEPAD_AXIS_LEFT_X))
            stick_y = self.check_joystick_dead_zone(get_gamepad_axis_movement(0, GAMEPAD_AXIS_LEFT_Y))
            # check for controller movement
            if any((stick_x,stick_y)):
                direction_x = stick_x
                direction_y = stick_y

        return Vector2(direction_x, direction_y)

    def input_pressed(self, action: str) -> bool:
        if self.input_cooldown_timer.active:
            return False
        key = self.keyboard_bindings.get(action)
        button = self.controller_bindings.get(action)

        if key is not None and is_key_pressed(key):
            return True
        if button is not None and is_gamepad_available(0) and is_gamepad_button_pressed(0, button):
            return True
        return False

    def input_down(self, action: str) -> bool:
        key = self.keyboard_bindings.get(action)
        button = self.controller_bindings.get(action)

        if key is not None and is_key_down(key):
            return True
        if button is not None and is_gamepad_available(0) and is_gamepad_button_down(0, button):
            return True
        return False

    # --- Audio System ---
    def play_music(self, key: str, restart: bool = False) -> None:
        stripped_key = key.strip('0123456789')
        if self.current_key == stripped_key and not restart:
            return  # Already playing this track!

        if self.current_track:
            stop_music_stream(self.current_track)

        if stripped_key in self.music:
            self.current_key = stripped_key
            self.current_track = self.music[stripped_key]
            play_music_stream(self.current_track)

    def pause_music(self) -> None:
        if self.current_track:
            pause_music_stream(self.current_track)

    def resume_music(self) -> None:
        if self.current_track:
            resume_music_stream(self.current_track)

    def play_sfx(self, key: str, pitch_variation: float = 0.0) -> None:
            if key in self.sfx:
                sound = self.sfx[key]
                if pitch_variation > 0:
                    var = get_random_value(-int(pitch_variation * 100), int(pitch_variation * 100)) / 100.0
                    set_sound_pitch(sound, 1.0 + var)
                play_sound(sound)

    def set_volumes(self) -> None:
        # --- music volumes ---
        for track in MUSIC_VOLUMES.keys():
            set_music_volume(self.music[track], MUSIC_VOLUMES[track] * MASTER_VOLUME)

        # --- sfx volumes ---
        for sound in SFX_VOLUMES.keys():
            set_sound_volume(self.sfx[sound], SFX_VOLUMES[sound] * MASTER_VOLUME)

    # --- Time System ---
    def update_play_time(self) -> None:
        if self.state == 'play':
            self.play_time = self.runtime - self.play_start - self.total_paused

    def pause_play_time(self) -> None:
        self.pause_start = self.runtime

    def resume_play_time(self) -> None:
        self.total_paused += self.runtime - self.pause_start

    @property
    def runtime(self) -> float:
        return get_time()

# --- EXECUTE LIFECYCLE ---
if __name__ == '__main__':
    game = Game()
    game.run()
    game.save_runtime()
    game.save_game_data()
    game.save_user_bindings()
    # --- Cleanup ---
    close_window()
    close_audio_device()
    sys.exit()
