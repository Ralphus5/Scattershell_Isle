from level import *

class Game:
    def __init__(self) -> None:
        self.init_raylib()
        self.init_paths()
        self.import_graphics()
        self.import_audio()
        self.import_world_data()
        self.set_volumes()
        self.init_game_state()

    def run(self) -> None:
        while not window_should_close():
            update_music_stream(self.current_track)
            dt = get_frame_time()
            self.input()
            self.set_game_mode()
            if self.state == 'title':
                self.title_screen()
            elif self.state == 'play':
                update_play_time(self)
                self.level.run(dt)
            elif self.state == 'pause':
                self.pause_menu()
            #debug(self, self.font, f"Play time: {self.play_time:.2f} | Total time: {self.runtime:.2f}")  # DEBUGGING
            self.draw_virtual_screen()

    def input(self) -> None:
        # --- universal input ---
        if is_action_pressed('fullscreen'):
            toggle_fullscreen()
            hide_cursor() if is_window_fullscreen() else show_cursor()

        # --- title ---
        if self.state == 'title':
            if is_action_pressed('pause') or is_key_pressed(KEY_ENTER):
                self.requested_state = 'play'

        # --- play ---
        elif self.state == 'play':
            if is_action_pressed('pause'):
                self.requested_state = 'pause'

        # --- pause ---
        elif self.state == 'pause':
            if is_action_pressed('pause'):
                self.requested_state = 'play'

    def set_game_mode(self) -> None:
        if not self.requested_state or self.requested_state == self.state:
            return
        old, new = self.state, self.requested_state
        self.requested_state = ''
        self.state = new

        # --- title ---
        if new == 'title':
            pass

        elif new == 'play':
            if old == 'title':
                self.play_start = get_time()
                self.level = Level(self)
            elif old == 'pause':
                resume_play_time(self)
                resume_music_stream(self.current_track)

        elif new == 'pause':
            if old == 'play':
                pause_play_time(self)
                pause_music_stream(self.current_track)

    def title_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLUE)
        draw_rectangle(444,444,444,444,RED)
        end_texture_mode()

    def pause_menu(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        self.level.draw_sprites()
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['pause_menu_tint'])
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

# --- Initialization steps ---

    def init_raylib(self) -> None:
        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_NAME)
        init_audio_device()
        set_target_fps(TARGET_FPS)
        set_exit_key(0)
        self.virtual_screen = load_render_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
        #toggle_fullscreen() # um mit fullscreen zu starten

    def init_paths(self) -> None:
        # --- detect running mode ---
        if getattr(sys, "frozen", False):
            base_dir = sys._MEIPASS # type: ignore
            user_dir = os.path.expanduser(join('~', 'Documents', GAME_NAME))
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            user_dir = join(base_dir, 'data')

        # --- create save directory if needed ---
        os.makedirs(user_dir, exist_ok=True)

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

    def import_graphics(self) -> None:

        self.graphics: dict[str, Image | Texture | list[Texture]] = {
            'icon': load_image(join(self.GRAPHICS_DIR, 'icon.png')),
            'player': load_texture(join(self.GRAPHICS_DIR, 'entities', 'player', 'player.png')),
            'overworld': load_texture(join(self.GRAPHICS_DIR, 'levels', 'overworld.png')),
            'cave': load_texture(join(self.GRAPHICS_DIR, 'levels', 'cave.png')),
            'cave2': load_texture(join(self.GRAPHICS_DIR, 'levels', 'cave2.png')),
            'column': load_texture(join(self.GRAPHICS_DIR, 'objects', 'column.png')),
            'rocks': import_image_folder(join(self.GRAPHICS_DIR, 'objects', 'rocks')),
            'grass': import_image_folder(join(self.GRAPHICS_DIR, 'objects', 'grass')),
            }

        self.font = load_font(join(self.FONTS_DIR, 'Pixelbasel.ttf'))

    def import_audio(self) -> None:
        # --- music ---
        self.music: dict[str, Music] = {
            'title_screen': load_music_stream(join(self.MUSIC_DIR, 'overworld.mp3')),
            'overworld': load_music_stream(join(self.MUSIC_DIR, 'overworld.mp3')),
            'cave': load_music_stream(join(self.MUSIC_DIR, 'cave.ogg')),
        }

        # --- sfx ---
        self.sfx: dict[str, Sound] = {
            'transition': load_sound(join(self.SFX_DIR, 'transition.wav')),
        }

    def import_world_data(self) -> None:
        self.maps: dict[str, TiledMap] = {
            'overworld': TiledMap(join(self.DATA_DIR, 'maps', 'overworld.tmx')),
            'cave': TiledMap(join(self.DATA_DIR, 'maps', 'cave.tmx')),
            'cave2': TiledMap(join(self.DATA_DIR, 'maps', 'cave2.tmx')),
            }

    def set_volumes(self) -> None:
        # --- music volumes ---
        for track in MUSIC_VOLUMES.keys():
            set_music_volume(self.music[track], MUSIC_VOLUMES[track])

        # --- sfx volumes ---
        for sound in SFX_VOLUMES.keys():
            set_sound_volume(self.sfx[sound], SFX_VOLUMES[sound])

    def init_game_state(self) -> None:
        set_window_icon(cast(Image, self.graphics['icon']))
        # state management
        self.state = ''
        self.requested_state = 'title'
        # time management
        self.play_time = 0.0
        self.play_start = 0.0
        self.pause_start = 0.0
        self.total_paused = 0.0
        # music
        self.current_track: Music = self.music['title_screen']
        play_music_stream(self.current_track)

    @property
    def runtime(self) -> float:
        return get_time()

if __name__ == '__main__':
    game = Game()
    game.run()
    # --- Cleanup ---
    close_window()
    close_audio_device()
    exit()
