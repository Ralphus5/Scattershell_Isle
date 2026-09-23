from player import *

class MenuTab:
    def __init__(self, game: Game, menu_name: str) -> None:
        self.game = game
        self.menu_name = menu_name
        self.clickable_entities: list[ClickableText] = []
        self.static_texts: list[RegularText] = []
        self.hover_id = -1

        # --- Assign Layout  ---
        match self.menu_name:
            case "Title" | "Settings":
                self.layout = "vertical"
            case "Play":
                self.layout = "vertical"
            case "Save & Quit":
                self.layout = "horizontal"
            case "Controls":
                self.layout = "grid"
            case "Audio":
                self.layout = "audio"

        # --- Populate entities ---
        match self.menu_name:
            case "Title":
                for text in enumerate(["Play", "Settings", "Close Game"]):
                    self.clickable_entities.append(ClickableText(game, text[1], game.fonts['title_menu_clickable_text'], FONT_SIZES['title_menu_clickable_text'], 0, (SCREEN_CENTER[0], (SCREEN_CENTER[1] - 390/2) + text[0] * 140), COLORS['title_menu_button'], COLORS['title_menu_button_hovered'], COLORS['title_menu_button_shadow']))
            case "Play":
                self.save_slot_rects = [Rectangle(SCREEN_CENTER[0] - 400, (SCREEN_CENTER[1] - 195) + 180 * i, 800, 120) for i in range(0, 3)]
            case "Settings":
                buttons = ["Audio", "Controls", "Save & Quit"] if self.game.state != 'title' else ["Audio", "Controls", "Back"]
                start_pos = SCREEN_CENTER[1] - 95
                for text in enumerate(buttons):
                    self.clickable_entities.append(ClickableText(game, text[1], game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (SCREEN_CENTER[0], start_pos + text[0] * 140), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
            case "Audio":
                if game.current_track:
                    set_music_volume(game.current_track, MUSIC_VOLUMES[cast(str, game.current_key)] * game.master_volume)
                self.static_texts.append(self.game.audio_text)
                self.clickable_entities.append(ClickableText(game, "Back", game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (SCREEN_CENTER[0], (SCREEN_CENTER[1] + 200)), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
                self.master_volume_rect = Rectangle(140, 200, 1000, 250)
                self.master_volume_rect_hovered = False
            case "Controls":
                self.static_texts.append(self.game.keyboard_bindings_note)
                self.static_texts.append(self.game.keyboard_bindings_prompt)
                self.clickable_entities.append(ClickableText(game, "Reset to defaults", game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (SCREEN_CENTER[0], 185), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
                y = 285
                for action in enumerate(DEFAULT_KEYBOARD_BINDINGS.keys()):
                    if action[1] in REMAPPABLE_ACTIONS:
                        self.clickable_entities.append(ClickableText(game, action[1].replace("_", " ").title(), self.game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (350 + 580 * int(action[0] / 4), y - 280 * int(action[0] / 4)), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
                        y += 70
                self.clickable_entities.append(ClickableText(game, "Back", game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (SCREEN_CENTER[0], SCREEN_CENTER[1] + 270), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
                self.clickable_entities.sort(key=attrgetter('pos.y'))
            case "Save & Quit":
                self.static_texts.append(self.game.save_and_quit_prompt)
                for text in enumerate(["Quit", "No"]):
                    self.clickable_entities.append(ClickableText(game, text[1], game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, ((SCREEN_CENTER[0] - 200) + text[0] * 400, SCREEN_CENTER[1] + 200), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
        
        self.menu_heading_size = measure_text_ex(self.game.fonts['menu_heading'], self.menu_name, FONT_SIZES['menu_heading'], 0)

    @property
    def item_count(self) -> int:
        if self.clickable_entities:
            return len(self.clickable_entities)
        if hasattr(self, 'save_slot_rects'):
            return len(self.save_slot_rects)
        return 0

    def navigate(self, direction: str) -> bool:
        old_hover = self.hover_id

        # Special Case: Audio Menu
        if self.layout == "audio":
            if direction == "up" and not self.master_volume_rect_hovered:
                self.hover_id = -1
                self.master_volume_rect_hovered = True
                return True
            elif direction == "down" and self.hover_id != 0:
                self.hover_id = 0
                self.master_volume_rect_hovered = False
                return True
            elif self.master_volume_rect_hovered and direction in ("left", "right"):
                step = 0.1 if direction == "right" else -0.1
                self.game.master_volume = clamp(round(self.game.master_volume + step, 2), 0.0, 1.0)
                self.game.set_volumes()
                self.game.save_settings()
                self.game.play_sfx('menu_button_pressed')
                return False
            return False

        if self.item_count == 0:
            return False

        # Vertical Layout (Title, Settings, Save Slots)
        if self.layout == "vertical":
            if direction == "up":
                self.hover_id = self.item_count - 1 if self.hover_id == -1 else (self.hover_id - 1) % self.item_count
            elif direction == "down":
                self.hover_id = 0 if self.hover_id == -1 else (self.hover_id + 1) % self.item_count

        # Horizontal Layout (Save & Quit)
        elif self.layout == "horizontal":
            if direction == "right":
                self.hover_id = 0 if self.hover_id == -1 else (self.hover_id + 1) % self.item_count
            elif direction == "left":
                self.hover_id = self.item_count - 1 if self.hover_id == -1 else (self.hover_id - 1) % self.item_count

        # 2D Grid Layout (Controls)
        elif self.layout == "grid":
            cols = 2
            if direction == "right":
                self.hover_id = 0 if self.hover_id == -1 else (self.hover_id + 1) % self.item_count
            elif direction == "left":
                self.hover_id = self.item_count - 1 if self.hover_id == -1 else (self.hover_id - 1) % self.item_count
            elif direction == "up":
                if self.hover_id == -1:
                    self.hover_id = self.item_count - 1
                else:
                    self.hover_id = (self.hover_id - cols) % self.item_count if self.hover_id - cols >= 0 else (self.hover_id - 1) % self.item_count
            elif direction == "down":
                if self.hover_id == -1:
                    self.hover_id = 0
                else:
                    self.hover_id = (self.hover_id + cols) % self.item_count if self.hover_id + cols < self.item_count else (self.hover_id + 1) % self.item_count

        return self.hover_id != old_hover

    def confirm(self) -> None:
        if self.menu_name == "Play" and self.hover_id != -1:
            self.game.play_sfx('menu_button_pressed')
            self.game.current_save_slot = self.hover_id + 1
            self.game.swipe_to_black_timer.activate()
            self.game.requested_state = 'play'
        elif self.clickable_entities:
            for entity in self.clickable_entities:
                entity.clicked = entity.hovered

    def update(self) -> None:
        self.draw()
        if not self.clickable_entities:
            return

        if self.hover_id != -1:
            self.hover_id = self.hover_id % len(self.clickable_entities)

        # --- Update Prompt Text ---
        if self.menu_name == "Controls" and self.game.keyboard_bindings_prompt.text != "Press key to assign...(ESC to cancel)":
            hovered_entity = self.clickable_entities[self.hover_id] if self.hover_id != -1 else None
            if hovered_entity:
                action_key = hovered_entity.text.replace(" ", "_").lower()
                if action_key in REMAPPABLE_ACTIONS:
                    bound_key = self.game.keyboard_bindings.get(action_key)
                    prompt_text = KEY_TO_NAME.get(bound_key, "...") # type: ignore
                else:
                    prompt_text = "..."
            else:
                prompt_text = "..."

            if self.game.keyboard_bindings_prompt.text != prompt_text:
                self.game.keyboard_bindings_prompt.text = prompt_text
                self.game.keyboard_bindings_prompt.set_position_and_size()

        # --- Update Hover ---
        for i, entity in enumerate(self.clickable_entities):
            entity.controller_hovered = (i == self.hover_id)
            entity.update()
            if entity.clicked:
                entity.clicked = False
                match entity.text:
                    case "Quit": 
                        assert isinstance(self.game.current_save_slot, int)
                        self.game.save_save_data(self.game.current_save_slot)
                        self.game.swipe_to_black_timer.activate()
                        self.game.requested_state = 'title'
                    case "No":
                        self.game.current_menu_tab = MenuTab(self.game, "Settings")
                    case "Back":
                        if self.game.state == 'pause':
                            if self.menu_name == "Audio" and self.game.current_track:
                                set_music_volume(self.game.current_track, MUSIC_VOLUMES[cast(str, self.game.current_key)] * self.game.master_volume * MUSIC_PAUSE_DIM_FACTOR)
                            self.game.current_menu_tab = MenuTab(self.game, "Settings")
                        elif self.game.state == 'title':
                            self.game.current_menu_tab = MenuTab(self.game, "Settings" if self.menu_name in ("Audio", "Controls") else "Title")
                    case "Audio":
                        if self.game.current_track:
                            set_music_volume(self.game.current_track, MUSIC_VOLUMES[cast(str, self.game.current_key)] * self.game.master_volume)
                        self.game.current_menu_tab = MenuTab(self.game, entity.text)
                    case "Close Game":
                        self.game.running = False
                        self.game.swipe_to_black_timer.activate() 
                    case _:
                        if entity.text.replace(" ", "_").lower() in REMAPPABLE_ACTIONS:
                            self.game.keyboard_bindings_prompt.text = "Press key to assign...(ESC to cancel)"
                            self.game.keyboard_bindings_prompt.set_position_and_size()
                        elif entity.text == "Reset to defaults":
                            self.game.keyboard_bindings.update(DEFAULT_KEYBOARD_BINDINGS)
                            self.game.save_settings()
                        else:
                            self.game.current_menu_tab = MenuTab(self.game, entity.text)
            entity.draw()

    def draw(self) -> None:
        if not self.menu_name == "Title":
            draw_texture(self.game.ui_images['menu_card'], 0, 0, WHITE)
            draw_text_ex(self.game.fonts['menu_heading'], self.menu_name, Vector2(SCREEN_CENTER[0] - self.menu_heading_size.x/2, SCREEN_CENTER[1] - 325), FONT_SIZES['menu_heading'], 0, COLORS['pause_menu_heading'])

        if self.menu_name in self.game.pause_menu_tab_names and self.game.state == 'pause':
            draw_triangle(Vector2(382,47), Vector2(332,72), Vector2(382,102), COLORS['pause_menu_button_shadow'])
            draw_triangle(Vector2(380,45), Vector2(330,70), Vector2(380,100), COLORS['pause_menu_button_hovered'] if self.game.input_pressed('switch_menu_tab_left') else COLORS['pause_menu_heading'])
            draw_triangle(Vector2(902,47), Vector2(902,102), Vector2(952,72), COLORS['pause_menu_button_shadow'])
            draw_triangle(Vector2(900,45), Vector2(900,100), Vector2(950,70), COLORS['pause_menu_button_hovered'] if self.game.input_pressed('switch_menu_tab_right') else COLORS['pause_menu_heading'])

        if hasattr(self, 'master_volume_rect'):
            draw_rectangle_rec(self.master_volume_rect, COLORS['master_volume_rect_hovered'] if self.master_volume_rect_hovered else COLORS['master_volume_rect'])
            draw_rectangle_lines_ex(self.master_volume_rect, 4, COLORS['master_volume_rect_outline'])
            
            line_start_x = 300
            line_length = SCREEN_WIDTH - 600
            draw_line_ex(Vector2(line_start_x, 360), Vector2(line_start_x + line_length, 360), 4, COLORS['master_volume_line'])
            
            # Synchronize handle x-position dynamically with self.game.master_volume
            volume_sync_x = int(line_start_x + (self.game.master_volume * line_length))
            draw_rectangle(volume_sync_x - 5, 360 - 15, 10, 30, COLORS['master_volume_line'])

        if self.menu_name == "Play":
            for i, rect in enumerate(self.save_slot_rects):
                is_hovered = (self.hover_id == i)
                
                bg_color = COLORS['save_slot_rects_hovered'] if is_hovered else COLORS['save_slot_rects']
                draw_rectangle_rec(rect, bg_color)
                draw_rectangle_lines_ex(rect, 4 if is_hovered else 2, COLORS['save_slot_rects_outline'])
                
                slot_title = f"Save {i + 1}"
                draw_text_ex(self.game.fonts['save_slot_title'], slot_title, Vector2(rect.x + 20, rect.y + 15), FONT_SIZES['save_slot_title'], 0, BLACK)

                summary = self.game.save_summaries[i + 1]
                if summary:
                    draw_text_ex(self.game.fonts['save_slot_info'], F"Time played: {timedelta(seconds=round(summary['play_time']))}", Vector2(rect.x + 20, rect.y + 55), FONT_SIZES['save_slot_info'], 0, COLORS['save_slot_info'])
                    draw_text_ex(self.game.fonts['save_slot_info'], F"Last saved: {summary['last_saved']}", Vector2(rect.x + 20, rect.y + 85), FONT_SIZES['save_slot_info'], 0, COLORS['save_slot_info'])
                    draw_text_ex(self.game.fonts['save_slot_info'], F"Current Location: {summary['current_map']}", Vector2(rect.x + 400, rect.y + 85), FONT_SIZES['save_slot_info'], 0, COLORS['save_slot_main_info'])
                else:
                    draw_text_ex(self.game.fonts['save_slot_new_game'], "--- NEW GAME ---", Vector2(rect.x + 176, rect.y + 40), FONT_SIZES['save_slot_new_game'], 0, COLORS['save_slot_new_game'])

        for text in self.static_texts:
            text.draw()
