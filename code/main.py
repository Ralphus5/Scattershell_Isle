from level import *

class Game:
    def __init__(self) -> None:
        self.init_raylib()
        self.init_paths()
        self.import_boot_assets()
        self.init_state()
        self.fade_from_black_timer.activate(0.5)
        self.load_generator = self.import_game_assets_and_saves()
        set_exit_key(0)

# --- GAME LOOP ---
    def run(self) -> None:
        while self.running and not window_should_close() or self.swipe_to_black_timer.active:
            # --- Setup ---
            dt = get_frame_time()
            for timer in self.timers:
                timer.update()
            self.get_general_input()
            self.change_game_mode()
            if self.current_track: update_music_stream(self.current_track)
            self.update_play_time()
            # --- Game Mode ---
            if self.state == 'boot':
                self.boot_screen(dt)
            elif self.state == 'title':
                self.title_screen()
            elif self.state == 'play':
                self.level.run(dt)
            elif self.state == 'pause':
                self.pause_menu()
            elif self.state == 'game_over':
                self.game_over_screen()
            self.swipe_to_black()
            self.fade_black()
            # --- Debugging ---
            #debug(self, self.debugging_font, f"Play time: {self.play_time:.2f} | Total time: {self.runtime:.2f}")
            #if hasattr(self, 'level'): 
                #debug(self, self.debugging_font, f"Sprites : {len(self.level.sprites)}", 10, 65)
                #debug(self, self.debugging_font, f"Health : {self.level.player.health}", 10, 120)
            # --- Update Frame ---
            if self.running or self.swipe_to_black_timer.active:
                self.draw_virtual_screen()

    def get_general_input(self) -> None:
        # --- Universal Input ---
        if self.input_pressed('fullscreen'):
            toggle_fullscreen()
            hide_cursor() if is_window_fullscreen() else show_cursor()

        if self.swipe_to_black_timer.active or self.fade_to_black_timer.active or self.fade_from_black_timer.active: # stop all further input during fading
            return
        
        # --- TITLE ---
        if self.state == 'title':
            # --- Click Title ---
            if not self.current_menu_tab:
                if (self.input_pressed('confirm') or self.input_pressed('open_map') or self.input_pressed('open_inventory') or self.input_pressed('menu_back')):
                    self.play_sfx('title_click')
                    self.current_menu_tab = MenuTab(self, 'Title')

            # --- Menus ---
            else:
                if self.current_menu_tab.menu_name == "Play":
                    if self.input_pressed('menu_move_up'):
                        self.play_sfx('menu_button_hovered')
                        if self.current_menu_tab.hover_id == -1:
                            self.current_menu_tab.hover_id = 2
                        else:
                            self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id - 1) % 3

                    elif self.input_pressed('menu_move_down'): 
                        self.play_sfx('menu_button_hovered')
                        if self.current_menu_tab.hover_id == -1:
                            self.current_menu_tab.hover_id = 0
                        else:
                            self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id + 1) % 3
                            
                    if self.current_menu_tab.hover_id != -1 and self.input_pressed('confirm'):
                        self.play_sfx('menu_button_pressed')
                        self.current_save_slot = self.current_menu_tab.hover_id + 1
                        self.swipe_to_black_timer.activate()
                        self.requested_state = 'play'
                        return
                    
                button_was_reassigned = False
                if self.keyboard_bindings_prompt.text == "Press key to assign...(ESC to cancel)":
                    if self.input_pressed('menu_back'):
                        self.keyboard_bindings_prompt.text = self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text
                        self.keyboard_bindings_prompt.set_position_and_size()
                    else:
                        for key in KEY_TO_NAME.keys():
                            if is_key_pressed(key) and not key in NON_REMAPPABLE_KEYS:
                                if self.current_menu_tab.hover_id in (6, 8) and key in NON_MAPPABLE_KEYS_TO_PAUSE:
                                    print(f"Cannot assign {KEY_TO_NAME[key]} to 'open map' or 'open inventory' due to menu navigation conflicts!") # create warning text???
                                else:
                                    self.keyboard_bindings[self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text.replace(" ", "_").lower()] = key
                                    self.keyboard_bindings_prompt.text = self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text
                                    self.keyboard_bindings_prompt.set_position_and_size()
                                    self.save_settings()
                                    button_was_reassigned = True
                num_items = len(self.current_menu_tab.clickable_entities)

                if self.input_pressed('confirm'):
                    for entity in self.current_menu_tab.clickable_entities:
                        entity.clicked = entity.hovered

                if self.input_pressed('open_inventory') or self.input_pressed('open_map') or self.input_pressed('menu_back'):
                    self.current_menu_tab = MenuTab(self, "Title" if not self.current_menu_tab.menu_name in ("Controls", "Audio") else "Settings")

                if self.current_menu_tab.menu_name in ('Title', 'Settings', 'Audio'):
                    if self.current_menu_tab.menu_name != 'Audio':
                        if self.input_pressed('menu_move_up'):
                            if self.current_menu_tab.hover_id == -1:
                                self.current_menu_tab.hover_id = 0 if self.current_menu_tab.menu_name == 'Title' else num_items - 1  # Select first item at title tab else last item
                            else:
                                self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id - 1) % num_items

                        elif self.input_pressed('menu_move_down'): 
                            if self.current_menu_tab.hover_id == -1:
                                self.current_menu_tab.hover_id = 0  # Select first item
                            else:
                                self.current_menu_tab.hover_id = (self.current_menu_tab.hover_id + 1) % num_items
                    else:
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
                        prompt_text = "..."
                        for entity in self.current_menu_tab.clickable_entities:
                            if entity.hovered and entity.text not in ("Back", "Reset to defaults"):
                                action_key = entity.text.replace(" ", "_").lower()
                                if action_key in self.keyboard_bindings:
                                    prompt_text = KEY_TO_NAME[self.keyboard_bindings[action_key]]
                                break

                        # Recalculate size and center whenever the displayed text changes
                        if self.keyboard_bindings_prompt.text != prompt_text:
                            self.keyboard_bindings_prompt.text = prompt_text
                            self.keyboard_bindings_prompt.set_position_and_size()

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
                self.current_menu_tab = MenuTab(self, self.main_settings_tab_names[self.current_menu_tab_id])
 
        # --- PAUSE ---
        elif self.state == 'pause':
            assert self.current_menu_tab is not None
            # --- Main Tabs ---
            # unpause
            if self.current_menu_tab.menu_name in self.main_settings_tab_names: # type: ignore
                if self.input_pressed('open_inventory') or self.input_pressed('open_map') or self.input_pressed('menu_back'):
                    self.requested_state = 'play'

                # switch tab
                elif self.input_pressed('switch_menu_tab_right'):
                    self.current_menu_tab_id = (self.current_menu_tab_id + 1) % len(self.main_settings_tab_names)
                    self.current_menu_tab = MenuTab(self, self.main_settings_tab_names[self.current_menu_tab_id])
                    self.play_sfx('menu_button_pressed')
                elif self.input_pressed('switch_menu_tab_left'):
                    self.current_menu_tab_id = (3 if self.current_menu_tab_id - 1 == 0 else self.current_menu_tab_id - 1) % len(self.main_settings_tab_names)
                    self.current_menu_tab = MenuTab(self, self.main_settings_tab_names[self.current_menu_tab_id])
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
                        self.keyboard_bindings_prompt.set_position_and_size()
                    else:
                        for key in KEY_TO_NAME.keys():
                            if is_key_pressed(key) and not key in NON_REMAPPABLE_KEYS:
                                if self.current_menu_tab.hover_id in (6, 8) and key in NON_MAPPABLE_KEYS_TO_PAUSE:
                                    print(f"Cannot assign {KEY_TO_NAME[key]} to 'open map' or 'open inventory' due to menu navigation conflicts!") # create warning text???
                                else:
                                    self.keyboard_bindings[self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text.replace(" ", "_").lower()] = key
                                    self.keyboard_bindings_prompt.text = self.current_menu_tab.clickable_entities[self.current_menu_tab.hover_id].text
                                    self.keyboard_bindings_prompt.set_position_and_size()
                                    self.save_settings()
                                    button_was_reassigned = True
                    
                # go back to main menu tabs
                elif self.input_pressed('open_inventory') or self.input_pressed('open_map') or self.input_pressed('menu_back'):
                    if self.current_menu_tab.menu_name == "Audio" and self.current_track:
                        set_music_volume(self.current_track, MUSIC_VOLUMES[cast(str, self.current_key)] * self.master_volume * MUSIC_PAUSE_DIM_FACTOR)
                    self.current_menu_tab = MenuTab(self, self.main_settings_tab_names[self.current_menu_tab_id])

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
                        prompt_text = "..."
                        for entity in self.current_menu_tab.clickable_entities:
                            if entity.hovered and entity.text not in ("Back", "Reset to defaults"):
                                action_key = entity.text.replace(" ", "_").lower()
                                if action_key in self.keyboard_bindings:
                                    prompt_text = KEY_TO_NAME[self.keyboard_bindings[action_key]]
                                break

                        # Recalculate size and center whenever the displayed text changes
                        if self.keyboard_bindings_prompt.text != prompt_text:
                            self.keyboard_bindings_prompt.text = prompt_text
                            self.keyboard_bindings_prompt.set_position_and_size()

        # --- GAME OVER ---
        elif self.state == 'game_over':
            if self.input_pressed('confirm') or self.input_pressed('open_inventory'):
                assert isinstance(self.current_save_slot, int)
                self.save_save_data(self.current_save_slot)
                self.requested_state = 'play'
            elif self.input_pressed('menu_back'):
                assert isinstance(self.current_save_slot, int)
                self.save_save_data(self.current_save_slot)
                self.swipe_to_black_timer.activate()
                self.requested_state = 'title'

    def change_game_mode(self) -> None:
        if not self.requested_state or self.requested_state == self.state or self.swipe_to_black_timer.active or self.fade_to_black_timer.active:
            return
        # --- Change state ---
        old, new = self.state, self.requested_state
        self.requested_state = ''
        self.state = new

        # --- Drain input buffer after menu switching ---
        self.input_cooldown_timer.activate()

        # --- TITLE ---
        if new == 'title':
            if self.current_menu_tab:
                self.current_menu_tab = None
            self.current_track = self.music['title']
            self.play_music('title')

        # --- PLAY ---
        elif new == 'play':
            if old == 'title':
                assert isinstance(self.current_save_slot, int)
                self.load_save_data(self.current_save_slot)
                self.level = Level(self, self.last_saved_current_map)
                # set player position if saved
                self.play_start = get_time()
                self.play_music(self.level.current_map, True)
                if self.current_track: set_music_volume(self.current_track, MUSIC_VOLUMES[cast(str, self.current_key)] * self.master_volume)
                self.fade_from_black_timer.activate(FADE_FROM_BLACK_AFTER_MENU_DURATION)
            elif old == 'pause':
                self.current_menu_tab_id = 0
                self.resume_play_time()
                if self.current_track:
                    set_music_volume(self.current_track, MUSIC_VOLUMES[cast(str, self.current_key)] * self.master_volume)
            elif old == 'game_over':
                assert isinstance(self.current_save_slot, int)
                self.load_save_data(self.current_save_slot)
                self.resume_play_time()
                self.level = Level(self, self.last_saved_current_map)
                self.play_music(self.level.current_map, True)
                self.fade_from_black_timer.activate(FADE_FROM_BLACK_AFTER_MENU_DURATION)

        # --- PAUSE ---
        elif new == 'pause':
            if old == 'play':
                self.pause_play_time()
                if self.current_track:
                    set_music_volume(self.current_track, MUSIC_VOLUMES[cast(str, self.current_key)] * self.master_volume * MUSIC_PAUSE_DIM_FACTOR)

        # --- GAME OVER ---
        elif new == 'game_over':
            self.pause_music()
            self.pause_play_time()

    def boot_screen(self, dt: float) -> None:
        # --- pull next import ---
        if not self.loading_finished:
            try:
                next(self.load_generator)
            except StopIteration:
                self.loading_finished = True

        # --- draw bootup animation ---
        begin_texture_mode(self.virtual_screen)
        clear_background(COLORS['boot_screen_background'])

        draw_texture(self.ralphus_studios_logo, SCREEN_CENTER[0] - self.ralphus_studios_logo.width//2, SCREEN_CENTER[1] - self.ralphus_studios_logo.height//2 - 50, WHITE)

        self.loading_status_text.draw()

        bar_width = 300
        bar_height = 12
        bar_x = (SCREEN_WIDTH - bar_width) / 2
        bar_y = SCREEN_HEIGHT - 50

        draw_rectangle_lines_ex(Rectangle(bar_x, bar_y, bar_width, bar_height), 2, COLORS['loading_bar_outline'])
        draw_rectangle_rec(Rectangle(bar_x + 2, bar_y + 2, (bar_width - 4) * self.loading_progress, bar_height - 4), COLORS['loading_bar_filling'])

        end_texture_mode()

        # --- switch to title ---
        if self.loading_finished and not self.boot_timer.active:
            self.requested_state = 'title'

    def title_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        draw_texture(self.ui_images['title_background'], 0, 0, WHITE)
        if not self.current_menu_tab:
            self.title_text.set_position_and_size(new_center=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 18 * sin(self.runtime * 3)))
            self.title_text.draw()
        else: 
            self.current_menu_tab.update()
        end_texture_mode()

    def pause_menu(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(BLACK)
        self.level.draw_sprites()
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['pause_menu_background'])            
        if self.current_menu_tab: 
            self.current_menu_tab.update()
        end_texture_mode()

    def game_over_screen(self) -> None:
        begin_texture_mode(self.virtual_screen)
        clear_background(COLORS['game_over_background'])

        self.game_over_text.draw()
        self.game_over_hint.draw()

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
        self.SAVE_FILES = {num: join(user_dir, f'save{num}.json') for num in [1,2,3]}
        # --- save files ---
        self.SETTINGS_FILE = join(saves_dir, 'settings.json')
        self.SAVE_FILES = {num: join(saves_dir, f'save{num}.json') for num in [1,2,3]}

    def import_boot_assets(self) -> None:
        self.icon: Image = load_image(join(self.GRAPHICS_DIR, 'ui', 'icon.png'))
        set_window_icon(self.icon)
        self.debugging_font = load_font_ex(join(self.FONTS_DIR, 'Pixelbasel.ttf'), FONT_SIZES['debugging'], ffi.NULL, 0)
        self.boot_font: Font = load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), FONT_SIZES['loading_bar_text'], ffi.NULL, 0)
        self.loading_status_text = RegularText(self, "Starting Game...", self.boot_font, FONT_SIZES['loading_bar_text'], 0, (SCREEN_CENTER[0], SCREEN_HEIGHT - 80), COLORS['loading_bar_text'])
        self.ralphus_studios_logo: Texture = load_texture(join(self.GRAPHICS_DIR, 'ui', 'ralphus_studios_logo.png'))

    def init_state(self) -> None:
        # --- State ---
        self.running = True
        self.state = 'boot'
        self.requested_state = ''
        self.swipe_to_black_timer = Timer(self, DEFAULT_SWIPE_TO_BLACK_DURATION, False, False)
        self.fade_from_black_timer = Timer(self, DEFAULT_FADE_FROM_BLACK_DURATION, False, False)
        self.fade_to_black_timer = Timer(self, DEFAULT_FADE_TO_BLACK_DURATION, False, False, False, self.fade_from_black_timer.activate)
        # --- Time ---
        self.timers: list[Timer] = []
        self.timers.append(self.swipe_to_black_timer)
        self.timers.append(self.fade_to_black_timer)
        self.timers.append(self.fade_from_black_timer)
        self.play_time = 0.0
        self.play_start = 0.0
        self.pause_start = 0.0
        self.total_paused = 0.0
        # --- Bootup & Loading State ---
        self.boot_timer = Timer(self, MIN_BOOT_DURATION, False, True, False)
        self.timers.append(self.boot_timer)
        self.loading_finished = False
        self.loading_progress = 0.0   # 0.0 bis 1.0 für Ladebalken
        # --- Menu Tabs ---
        self.current_menu_tab_id: int = 0 # 0 = map, 1 = inventory, 2 = settings
        self.current_menu_tab: Optional[MenuTab] = None
        self.main_settings_tab_names: list[str] = ["Map", "Inventory", "Settings"]
        # --- Input ---
        self.input_cooldown_timer = Timer(self, INPUT_COOLDOWN_AFTER_SWITCHING_GAME_MODE, False, False, False)
        self.timers.append(self.input_cooldown_timer)
        self.keyboard_bindings = dict(DEFAULT_KEYBOARD_BINDINGS)
        self.controller_bindings = dict(CONTROLLER_BINDINGS)
        # --- Audio ---
        self.current_key: Optional[str] = None
        self.current_track: Optional[Music] = None
        # --- Saves ---
        self.save_summaries: dict[int, dict | None] = {1: None, 2: None, 3: None}
        self.current_save_slot: Optional[int] = None

    def import_game_assets_and_saves(self) -> Generator:
        # --- Save Data ---
        self.loading_status_text.text = "Loading Save Data..."
        self.loading_status_text.set_position_and_size()
        self.loading_progress = 0.2
        yield
        self.load_settings()
        yield
        self.load_save_summaries()
        yield

        # --- Graphics ---
        self.loading_status_text.text = "Loading Graphics..."
        self.loading_status_text.set_position_and_size()
        self.loading_progress = 0.4
        yield
        yield from self.import_graphics()
        self.init_main_menu_texts()
        yield

        # --- Audio ---
        self.loading_status_text.text = "Loading Audio..."
        self.loading_status_text.set_position_and_size()
        self.loading_progress = 0.6
        yield
        yield from self.import_audio()
        self.set_volumes()
        yield

        # --- World Data ---
        self.loading_status_text.text = "Loading World Data..."
        self.loading_progress = 0.8
        yield from self.import_world_data()
        yield

        # --- Finished ---
        self.loading_status_text.text = "Finished!"
        self.loading_status_text.set_position_and_size()
        self.loading_progress = 1.0
        self.play_sfx('loading_finished')
        yield

    def import_graphics(self) -> Generator:
        self.sword_images: dict[str, Texture] = {}
        for direction in ['up', 'down', 'left', 'right']:
            self.sword_images[direction] = load_texture(join(self.GRAPHICS_DIR, 'sword', f'{direction}.png'))
            yield

        self.ui_images: dict[str, Texture] = {}
        for image in ['title_background', 'sword', 'menu_card']:
            self.ui_images[image] = load_texture(join(self.GRAPHICS_DIR, 'ui', f'{image}.png'))
            yield
        
        self.level_images: dict[str, Texture] = {}
        for image in ['start_area', 'cave', 'cave2']:
            self.level_images[image] = load_texture(join(self.GRAPHICS_DIR, 'levels', f'{image}.png'))
            yield

        self.tile_images: dict[str, list[Texture]] = {}
        for tile in ['column', 'rock', 'grass']:
            self.tile_images[tile] = import_image_folder(join(self.GRAPHICS_DIR, 'tiles', tile))
            yield

        self.entity_images: dict[str, dict[str, list[Texture]]] = {}
        for entity in ['player', 'bamboo', 'spirit', 'squid', 'raccoon']:
            if entity == 'player':
                self.entity_images['player'] = {
                    f'{direction}{suffix}': import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'player', f'{direction}{suffix}'))
                    for direction in ['down', 'right', 'left', 'up']
                    for suffix in ['', '_attack', '_idle']
                }
            else:
                self.entity_images[entity] = {
                    state: import_image_folder(join(self.GRAPHICS_DIR, 'entities', 'monsters', entity, state)) for state in ['move', 'idle', 'attack']
                }
            yield

        self.attack_animations_images: dict[str, list[Texture]] = {}
        for entity in ['raccoon', 'spirit', 'bamboo', 'squid']:
            self.attack_animations_images[entity] = import_image_folder(join(self.GRAPHICS_DIR, 'attack_animations', f'{entity}_attack'))
            yield

        self.death_animations_images: dict[str, list[Texture]] = {}
        for entity in ['player', 'raccoon', 'spirit', 'bamboo', 'squid']:
            self.death_animations_images[entity] = import_image_folder(join(self.GRAPHICS_DIR, 'death_animations', f'{entity}_death'))
            yield

        self.particles_images: dict[str, list[list[Texture]]] = {}
        for particle, variant_amount in [('leaf', 6)]:
            self.particles_images[particle] = []
            for variant in range(1, variant_amount + 1):
                self.particles_images[particle].append(import_image_folder(join(self.GRAPHICS_DIR, 'particles', f'{particle}{variant}')))
                yield 

        self.fonts: dict[str, Font] = {}
        for font in ['title', 'game_over', 'title_menu_clickable_text', 'menu_heading', 'settings_tab_clickable_text', 'master_volume', 'save_slot_title', 'save_slot_new_game']:
            self.fonts[font] = load_font_ex(join(self.FONTS_DIR, 'slkscr.ttf'), FONT_SIZES[font], ffi.NULL, 0)
            yield
        for font in ['game_over_hint', 'save_and_quit_prompt', 'keyboard_bindings_note', 'keyboard_bindings_prompt', 'save_slot_info']:
            self.fonts[font] = load_font_ex(join(self.FONTS_DIR, 'Pixelbasel.ttf'), FONT_SIZES[font], ffi.NULL, 0)
            yield

    def import_audio(self) -> Generator:
        # --- music ---
        self.music: dict[str, Music] = {}
        for music in MUSIC_VOLUMES.keys():
            self.music[music] = load_music_stream(join(self.MUSIC_DIR, f'{music}.wav'))
            yield

        # --- sfx ---
        self.sfx: dict[str, Sound] = {}
        for sfx in SFX_VOLUMES.keys():
            self.sfx[sfx] = load_sound(join(self.SFX_DIR, f'{sfx}.wav'))
            yield

    def import_world_data(self) -> Generator:
        self.maps: dict[str, TiledMap] = {}
        for map in ['start_area', 'cave', 'cave2']:
            self.maps[map] = TiledMap(join(self.DATA_DIR, 'maps', f'{map}.tmx'))
            yield

    def init_main_menu_texts(self) -> None:
        self.title_text = RegularText(self, GAME_NAME, self.fonts['title'], FONT_SIZES['title'], 0, SCREEN_CENTER, COLORS['title_text'], COLORS['title_text_shadow'])
        self.game_over_text = RegularText(self, "Game Over", self.fonts['game_over'], FONT_SIZES['game_over'], 0, SCREEN_CENTER, COLORS['game_over_text'], COLORS['game_over_text_shadow'])
        self.game_over_hint = RegularText(self, "Enter/Start: Play again\nEscape: Save & Quit", self.fonts['game_over_hint'], FONT_SIZES['game_over_hint'], 0, (SCREEN_CENTER[0], SCREEN_HEIGHT - 100), COLORS['game_over_hint'])
        self.save_and_quit_prompt = RegularText(self, "\t\t\t\t\t\t Quit game?\n(Progress will be saved.)", self.fonts['save_and_quit_prompt'], FONT_SIZES['save_and_quit_prompt'], 0, SCREEN_CENTER, COLORS['save_and_quit_prompt'])
        self.audio_text = RegularText(self, "-\t\tMaster Volume\t\t+", self.fonts['master_volume'], FONT_SIZES['master_volume'], 0, (SCREEN_CENTER[0], SCREEN_CENTER[1] - 100), COLORS['pause_menu_button'], COLORS['pause_menu_button_shadow'])
        self.keyboard_bindings_note = RegularText(self, "Keyboard only!", self.fonts['keyboard_bindings_note'], FONT_SIZES['keyboard_bindings_note'], 0, (SCREEN_WIDTH - 175, SCREEN_HEIGHT - 65), COLORS['keyboard_bindings_note'])
        self.keyboard_bindings_prompt = RegularText(self, "...", self.fonts['keyboard_bindings_prompt'], FONT_SIZES['keyboard_bindings_prompt'], 0, (SCREEN_CENTER[0], SCREEN_CENTER[1] + 210), COLORS['keyboard_bindings_prompt'])

    def load_settings(self) -> None:
        data = load_file(self.SETTINGS_FILE, "Loading settings")
        self.total_runtime = data.get('total_runtime', 0.0)
        self.master_volume: float = float(data.get('master_volume', MASTER_VOLUME))
        if 'keyboard_bindings' in data:
            self.keyboard_bindings.update(data['keyboard_bindings'])

    def load_save_summaries(self) -> None:
        for slot_id in [1,2,3]:
            if os.path.exists(self.SAVE_FILES[slot_id]):
                save_data = load_file(self.SAVE_FILES[slot_id])
                self.save_summaries[slot_id] = save_data.get('summary', {})
            else:
                self.save_summaries[slot_id] = None

    # --- Input System ---
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

    # --- Misc ---
    def load_save_data(self, slot_id: int) -> None:
        save_data = load_file(self.SAVE_FILES[slot_id])
        game_data = save_data.get('game_data', {})

        self.last_saved_current_map: str = game_data.get('current_map', 'start_area')

    def save_save_data(self, slot_id: int) -> None:
        if not hasattr(self, 'level'):
            return
        current_process = 'Saving game data to save file {slot_id}'

        old_save_data = load_file(self.SAVE_FILES[slot_id])

        accumulated_play_time = 0
        old_summary = old_save_data.get("summary", 0)
        if old_summary:
            accumulated_play_time = old_summary.get("play_time", 0)

        data_to_save = {
            "summary": {
                "current_map": self.level.current_map,
                "play_time": self.play_time + accumulated_play_time if accumulated_play_time else self.play_time,
                "last_saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
                # "player_health": self.level.player.health,
            },
            "game_data": {
                "current_map": self.level.current_map,
                # Add player inventory, position, defeated enemies, etc.
            }
        }

        save_file(self.SAVE_FILES[slot_id], data_to_save, current_process)
        self.save_summaries[slot_id] = data_to_save["summary"]

    def save_settings(self) -> None:
        current_process = "Saving settings"
        save_data = load_file(self.SETTINGS_FILE, current_process)

        # save runtime
        accumulated_time = self.total_runtime if hasattr(self, 'total_runtime') else 0.0
        save_data['total_runtime'] = self.runtime + accumulated_time

        # save audio settings
        save_data['master_volume'] = self.master_volume

        # save keybindings
        current_kb = {k: v for k, v in self.keyboard_bindings.items() if k in REMAPPABLE_ACTIONS}
        save_data['keyboard_bindings'] = current_kb

        save_file(self.SETTINGS_FILE, save_data, current_process)

    def swipe_to_black(self) -> None:
        if not self.swipe_to_black_timer.active:
            return

        progress = self.swipe_to_black_timer.elapsed_time / self.swipe_to_black_timer.duration
        bar_width = int(SCREEN_WIDTH * progress)
        begin_texture_mode(self.virtual_screen)
        draw_rectangle(0, 0, bar_width, SCREEN_HEIGHT, BLACK)
        end_texture_mode()

    def fade_black(self) -> None:
        if self.fade_to_black_timer.active:
            alpha = int((self.fade_to_black_timer.elapsed_time / self.fade_to_black_timer.duration) * 255)
            begin_texture_mode(self.virtual_screen)
            draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(0,0,0, alpha % 255))
            end_texture_mode()

        elif self.fade_from_black_timer.active:
            alpha_drain = int((self.fade_from_black_timer.elapsed_time / self.fade_from_black_timer.duration) * 255)
            begin_texture_mode(self.virtual_screen)
            draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(0, 0, 0, 255 - alpha_drain))
            end_texture_mode()

# --- EXECUTE LIFECYCLE ---
if __name__ == '__main__':
    game = Game()
    game.run()
    game.save_settings()
    # --- Cleanup ---
    close_audio_device()
    sys.exit()
    close_window()
