from level import *

class Game:
    def __init__(self) -> None:
        self.init_raylib()
        self.init_paths()
        self.import_graphics()
        self.import_audio()
        self.import_world_data()
        self.init_state()
        self.init_main_menu_texts()
        self.load_settings()
        self.load_save_data()
        self.set_volumes()
        set_window_icon(self.icon)
        set_exit_key(0)

# --- GAME LOOP ---
    def run(self) -> None:
        while self.running and not window_should_close():
            dt = get_frame_time()
            self.get_general_input()
            self.change_game_mode()
            if self.current_track: update_music_stream(self.current_track)
            self.update_play_time()
            self.handle_game_mode(dt)
            #debug(self, self.fonts['debugging'], f"Play time: {self.play_time:.2f} | Total time: {self.runtime:.2f}")  # DEBUGGING
            #if hasattr(self, 'level'): 
                #debug(self, self.fonts['debugging'], f"Sprites : {len(self.level.sprites)}", 10, 65)  # DEBUGGING
                #debug(self, self.fonts['debugging'], f"Health : {self.level.player.health}", 10, 120)  # DEBUGGING
            self.draw_virtual_screen()

    def get_general_input(self) -> None:
        self.input_cooldown_timer.update()
        # --- Universal Input ---
        if self.input_pressed('fullscreen'):
            toggle_fullscreen()
            hide_cursor() if is_window_fullscreen() else show_cursor()

        # --- TITLE ---
        if self.state == 'title':
            if self.input_pressed('confirm') or self.input_pressed('open_map') or self.input_pressed('open_inventory') or self.input_pressed('menu_back'):
                self.requested_state = 'play'

        # --- PLAY ---
        elif self.state == 'play':
            # enter pause state
            if self.input_pressed('open_map') or self.input_pressed('open_inventory') or (self.input_pressed('menu_back') and is_key_pressed(self.keyboard_bindings['menu_back'])):
                self.play_sfx('pause_menu_opened')
                self.requested_state = 'pause'
                if self.input_pressed('open_map'):
                    self.current_menu_tab_id = 0 
                elif self.input_pressed('open_inventory'):
                    self.current_menu_tab_id = 1
                elif self.input_pressed('menu_back'):
                    self.current_menu_tab_id = 2
                self.current_menu_tab = MenuTab(self, self.main_menu_tab_names[self.current_menu_tab_id])
 
        # --- PAUSE ---
        elif self.state == 'pause':
            assert self.current_menu_tab is not None
            # --- Main Tabs ---
            # unpause
            if self.current_menu_tab.menu_name in self.main_menu_tab_names: # type: ignore
                if self.input_pressed('open_inventory') or self.input_pressed('open_map') or self.input_pressed('menu_back'):
                    self.requested_state = 'play'

                # switch tab
                elif self.input_pressed('switch_menu_tab_right'):
                    self.current_menu_tab_id = (self.current_menu_tab_id + 1) % len(self.main_menu_tab_names)
                    self.current_menu_tab = MenuTab(self, self.main_menu_tab_names[self.current_menu_tab_id])
                    self.play_sfx('menu_button_pressed')
                elif self.input_pressed('switch_menu_tab_left'):
                    self.current_menu_tab_id = (3 if self.current_menu_tab_id - 1 == 0 else self.current_menu_tab_id - 1) % len(self.main_menu_tab_names)
                    self.current_menu_tab = MenuTab(self, self.main_menu_tab_names[self.current_menu_tab_id])
                    self.play_sfx('menu_button_pressed')

                # settings tab
                elif self.current_menu_tab and self.current_menu_tab.clickable_entities:
                    num_items = len(self.current_menu_tab.clickable_entities)

                    if self.input_pressed('menu_move_up'):
                        if self.current_menu_tab.hover_id == -1:
                            self.current_menu_tab.hover_id = num_items - 1  # Select last item
                        else:
                            self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id - 1) % num_items

                    elif self.input_pressed('menu_move_down'): 
                        if self.current_menu_tab.hover_id == -1:
                            self.current_menu_tab.hover_id = 0  # Select first item
                        else:
                            self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id + 1) % num_items

                    if self.current_menu_tab.menu_name == 'Settings':
                        if self.input_pressed('confirm'):
                            for entity in self.current_menu_tab.clickable_entities:
                                entity.clicked = entity.hovered

            # --- Sub Tabs ---
            else:
                button_was_reassigned = False
                if self.keyboard_bindings_prompt.text == "Press key to assign...(ESC to cancel)":
                    if self.input_pressed('menu_back'):
                        self.keyboard_bindings_prompt.text = self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text
                    else:
                        for key in KEY_TO_NAME.keys():
                            if is_key_pressed(key) and not key in NON_REMAPPABLE_KEYS:
                                if self.current_menu_tab.hover_id in (6, 8) and key in NON_MAPPABLE_KEYS_TO_PAUSE:
                                    print(f"Cannot assign {KEY_TO_NAME[key]} to 'open map' or 'open inventory' due to menu navigation conflicts!") # create warning text???
                                else:
                                    self.keyboard_bindings[self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text.replace(" ", "_").lower()] = key
                                    self.keyboard_bindings_prompt.text = self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text
                                    self.keyboard_bindings_prompt.update_position_and_size((SCREEN_CENTER[0], SCREEN_CENTER[1] + 200))
                                    self.save_settings()
                                    button_was_reassigned = True
                    
                # go back to main menu tabs
                elif self.input_pressed('open_inventory') or self.input_pressed('open_map') or self.input_pressed('menu_back'):
                    if self.current_menu_tab.menu_name == "Audio":
                        set_music_volume(self.current_track, MUSIC_VOLUMES[cast(str, self.current_key)] * self.master_volume * MUSIC_PAUSE_DIM_FACTOR)
                    self.current_menu_tab = MenuTab(self, self.main_menu_tab_names[self.current_menu_tab_id])

                # --- quit submenu ---
                if self.current_menu_tab.menu_name == "Save & Quit":
                    num_items = len(self.current_menu_tab.clickable_entities)
                    if self.input_pressed('menu_move_right'):
                        if self.current_menu_tab.hover_id == -1:
                            self.current_menu_tab.hover_id = num_items - 1  # Select last item
                        else:
                            self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id - 1) % num_items

                    elif self.input_pressed('menu_move_left'):
                        if self.current_menu_tab.hover_id == -1:
                            self.current_menu_tab.hover_id = 0  # Select first item
                        else:
                            self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id + 1) % num_items

                    elif self.input_pressed('confirm'):
                        for entity in self.current_menu_tab.clickable_entities:
                            entity.clicked = entity.hovered

                # --- audio submenu ---
                elif self.current_menu_tab.menu_name == "Audio":
                    if self.input_pressed('menu_move_up') and not self.current_menu_tab.master_volume_rect_hovered:
                        self.current_menu_tab.hover_id = -1
                        self.current_menu_tab.master_volume_rect_hovered = True
                        self.play_sfx('menu_button_hovered')
                    elif self.input_pressed('menu_move_down'):
                        self.current_menu_tab.hover_id = 0
                        self.current_menu_tab.master_volume_rect_hovered = False
                    elif self.input_pressed('confirm'):
                        self.current_menu_tab.clickable_entities[0].clicked = self.current_menu_tab.clickable_entities[0].hovered

                    if self.current_menu_tab.master_volume_rect_hovered:
                        volume_changed = False
                        if self.input_pressed('menu_move_right'):
                            self.master_volume = min(1.0, round(self.master_volume + 0.1, 2))
                            volume_changed = True
                        elif self.input_pressed('menu_move_left'):
                            self.master_volume = max(0.0, round(self.master_volume - 0.1, 2))
                            volume_changed = True

                        if volume_changed:
                            self.set_volumes()
                            self.save_settings()
                            self.play_sfx('menu_button_pressed')

                # --- controls submenu ---
                elif self.current_menu_tab.menu_name == "Controls":
                    if not self.keyboard_bindings_prompt.text == "Press key to assign...(ESC to cancel)" and not button_was_reassigned:
                        num_items = len(self.current_menu_tab.clickable_entities)
                        if self.input_pressed('menu_move_right'):
                            if self.current_menu_tab.hover_id == -1:
                                self.current_menu_tab.hover_id = num_items - 1  # Select last item
                            else:
                                self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id + 1) % num_items

                        elif self.input_pressed('menu_move_left'):
                            if self.current_menu_tab.hover_id == -1:
                                self.current_menu_tab.hover_id = 0  # Select first item
                            else:
                                self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id - 1) % num_items

                        elif self.input_pressed('menu_move_up'):
                            if self.current_menu_tab.hover_id == -1:
                                self.current_menu_tab.hover_id = num_items - 1  # Select last item
                            else:
                                self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id - 2) % num_items if self.current_menu_tab.hover_id - 2 >= 0 else (self.current_menu_tab.hover_id - 1) % num_items

                        elif self.input_pressed('menu_move_down'):
                            if self.current_menu_tab.hover_id == -1:
                                self.current_menu_tab.hover_id = 0  # Select first item
                            else:
                                self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id + 2) % num_items if self.current_menu_tab.hover_id + 2 < num_items else (self.current_menu_tab.hover_id + 1) % num_items

                        elif self.input_pressed('confirm') and not button_was_reassigned:
                            for entity in self.current_menu_tab.clickable_entities:
                                entity.clicked = entity.hovered

                    # update key prompt
                        self.keyboard_bindings_prompt.text = "..."
                        for entity in self.current_menu_tab.clickable_entities:
                            if entity.hovered and not entity.text in ("Back", "Reset to defaults"):
                                self.keyboard_bindings_prompt.text = KEY_TO_NAME[self.keyboard_bindings[entity.text.replace(" ", "_").lower()]]
                        self.keyboard_bindings_prompt.update_position_and_size((SCREEN_CENTER[0], SCREEN_CENTER[1] + 200))

        # --- GAME OVER ---
        elif self.state == 'game_over':
            if self.input_pressed('confirm') or self.input_pressed('open_inventory'):
                self.requested_state = 'play'

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
                self.current_menu_tab_id = 0
                self.resume_play_time()
                set_music_volume(self.current_track, MUSIC_VOLUMES[cast(str, self.current_key)] * self.master_volume)
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
                set_music_volume(self.current_track, MUSIC_VOLUMES[cast(str, self.current_key)] * self.master_volume * MUSIC_PAUSE_DIM_FACTOR)

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
            self.pause_menu(dt)
        elif self.state == 'game_over':
            self.game_over_screen()

    def title_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        draw_texture(self.background_images['title'], 0, 0, WHITE)
        self.title_text.draw()
        end_texture_mode()

    def pause_menu(self, dt: float) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        self.level.draw_sprites()
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['pause_menu_background'])            

        if self.current_menu_tab: 
            self.current_menu_tab.update(dt)

        end_texture_mode()

    def game_over_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)

        self.game_over_text.draw()

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
        self.icon: Image = load_image(join(self.GRAPHICS_DIR, 'ui', 'icon.png'))

        self.sword_images: dict[str, Texture] = {
            'down': load_texture(join(self.GRAPHICS_DIR, 'sword', 'down.png')),
            'up': load_texture(join(self.GRAPHICS_DIR, 'sword', 'up.png')),
            'right': load_texture(join(self.GRAPHICS_DIR, 'sword', 'right.png')),
            'left': load_texture(join(self.GRAPHICS_DIR, 'sword', 'left.png')),
        }

        self.ui_images: dict[str, Texture] = { 
            'sword': load_texture(join(self.GRAPHICS_DIR, 'sword', 'full.png')),
            'menu_card': load_texture(join(self.GRAPHICS_DIR, 'ui', 'menu_card.png')),
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
            'title': load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), FONT_SIZES['title'], ffi.NULL, 0),
            'game_over': load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), FONT_SIZES['game_over'], ffi.NULL, 0),
            'menu_heading': load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), FONT_SIZES['menu_heading'], ffi.NULL, 0),
            'settings_tab_clickable_text': load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), FONT_SIZES['settings_tab_clickable_text'], ffi.NULL, 0),
            'save_and_quit_prompt': load_font_ex(join(self.FONTS_DIR, 'Pixelbasel.ttf'), FONT_SIZES['save_and_quit_prompt'], ffi.NULL, 0),
            'master_volume': load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), FONT_SIZES['master_volume'], ffi.NULL, 0),
            'keyboard_bindings_note': load_font_ex(join(self.FONTS_DIR, 'Pixelbasel.ttf'), FONT_SIZES['keyboard_bindings_note'], ffi.NULL, 0),
            'keyboard_bindings_prompt': load_font_ex(join(self.FONTS_DIR, 'Pixelbasel.ttf'), FONT_SIZES['keyboard_bindings_prompt'], ffi.NULL, 0),
            'debugging': load_font_ex(join(self.FONTS_DIR, 'Pixelbasel.ttf'), FONT_SIZES['debugging'], ffi.NULL, 0),
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
            'menu_button_pressed': load_sound(join(self.SFX_DIR, 'menu_button_pressed.wav')),
            'pause_menu_opened': load_sound(join(self.SFX_DIR, 'pause_menu_opened.wav')),
            'menu_button_hovered': load_sound(join(self.SFX_DIR, 'menu_button_hovered.wav')),
        }

    def import_world_data(self) -> None:
        self.maps: dict[str, TiledMap] = {
            'start_area': TiledMap(join(self.DATA_DIR, 'maps', 'start_area.tmx')),
            'cave': TiledMap(join(self.DATA_DIR, 'maps', 'cave.tmx')),
            'cave2': TiledMap(join(self.DATA_DIR, 'maps', 'cave2.tmx')),
            }

    def init_state(self) -> None:
        # state
        self.running = True
        self.state = 'boot'
        self.requested_state = 'title'
        self.current_menu_tab_id: int = 0 # 0 = map, 1 = inventory, 2 = settings
        self.current_menu_tab: Optional[MenuTab] = None
        self.main_menu_tab_names: list[str] = ["Map", "Inventory", "Settings"]
        # time
        self.play_time = 0.0
        self.play_start = 0.0
        self.pause_start = 0.0
        self.total_paused = 0.0
        # input
        self.input_cooldown_timer = Timer(self, INPUT_COOLDOWN_AFTER_SWITCHING_GAME_MODE, False, False, False)
        self.keyboard_bindings = dict(DEFAULT_KEYBOARD_BINDINGS)
        self.controller_bindings = dict(CONTROLLER_BINDINGS)
        # audio
        self.current_key: Optional[str] = None
        self.current_track: Music = self.music['title']

    def init_main_menu_texts(self) -> None:
        self.title_text = RegularText(self, GAME_NAME, self.fonts['title'], FONT_SIZES['title'], 0, SCREEN_CENTER, COLORS['title_text'], COLORS['title_text_shadow'])
        self.game_over_text = RegularText(self, "Game Over", self.fonts['game_over'], FONT_SIZES['game_over'], 0, SCREEN_CENTER, COLORS['game_over_text'], COLORS['game_over_text_shadow'])
        self.save_and_quit_prompt = RegularText(self, "\t\t\t\t\t\t\t\t\t\tQuit game?\n(Progress is saved automatically.)", self.fonts['save_and_quit_prompt'], FONT_SIZES['save_and_quit_prompt'], 0, SCREEN_CENTER, COLORS['save_and_quit_prompt'])
        self.audio_text = RegularText(self, "-\t\tMaster Volume\t\t+", self.fonts['master_volume'], FONT_SIZES['master_volume'], 0, (SCREEN_CENTER[0], SCREEN_CENTER[1] - 100), COLORS['pause_menu_button'], COLORS['pause_menu_button_shadow'])
        self.keyboard_bindings_note = RegularText(self, "Keyboard only!", self.fonts['keyboard_bindings_note'], FONT_SIZES['keyboard_bindings_note'], 0, (SCREEN_WIDTH - 175, SCREEN_HEIGHT - 65), COLORS['keyboard_bindings_note'])
        self.keyboard_bindings_prompt = RegularText(self, "...", self.fonts['keyboard_bindings_prompt'], FONT_SIZES['keyboard_bindings_prompt'], 0, (SCREEN_CENTER[0], SCREEN_CENTER[1] + 200), COLORS['keyboard_bindings_prompt'])

    def save_settings(self) -> None:
        current_process = "Saving settings"
        save_data = load_file(self.SETTINGS_FILE, current_process)

        current_kb = {k: v for k, v in self.keyboard_bindings.items() if k in REMAPPABLE_ACTIONS}

        save_data['master_volume'] = self.master_volume
        save_data['keyboard_bindings'] = current_kb

        save_file(self.SETTINGS_FILE, save_data, current_process)

    def load_save_data(self) -> None:
        save_data = load_file(self.SAVE_FILE)
        self.total_runtime = save_data.get('total_runtime', 0.0)
        self.last_saved_current_map: str = save_data.get('current_map', 'start_area')

    # --- Input System ---
    def load_settings(self):
        data = load_file(self.SETTINGS_FILE, "Loading settings")
        self.master_volume: float = float(data.get('master_volume', MASTER_VOLUME))
        if 'keyboard_bindings' in data:
            self.keyboard_bindings.update(data['keyboard_bindings'])

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
            set_music_volume(self.music[track], MUSIC_VOLUMES[track] * self.master_volume)

        # --- sfx volumes ---
        for sound in SFX_VOLUMES.keys():
            set_sound_volume(self.sfx[sound], SFX_VOLUMES[sound] * self.master_volume)

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
    game.save_settings()
    # --- Cleanup ---
    close_window()
    close_audio_device()
    sys.exit()
