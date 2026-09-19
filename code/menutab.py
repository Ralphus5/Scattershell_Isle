from player import *

class MenuTab:
    def __init__(self, game: Game, menu_name: str) -> None:
        self.game = game
        self.menu_name = menu_name
        self.clickable_entities: list[ClickableText] = []
        self.static_texts: list[RegularText] = []
        self.hover_id = -1
        match self.menu_name:
            case "Map": # map
                pass
                #self.clickable_entities.append() 
            case "Inventory": # inventory
                pass
                #self.clickable_entities.append() 
            case "Settings": # settings
                for text in enumerate(["Audio", "Controls", "Save & Quit"]):
                    self.clickable_entities.append(ClickableText(game, text[1], game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (SCREEN_CENTER[0], (SCREEN_CENTER[1] - 190/2) + text[0] * 140), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
            case "Audio":
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
                self.clickable_entities.append(ClickableText(game, "Back", game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (SCREEN_CENTER[0] , SCREEN_CENTER[1] + 270), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
                self.clickable_entities.sort(key=attrgetter('pos.y'))
            case "Save & Quit":
                self.static_texts.append(self.game.save_and_quit_prompt)
                for text in enumerate(["Quit", "No"]):
                    self.clickable_entities.append(ClickableText(game, text[1], game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, ((SCREEN_CENTER[0] - 200) + text[0] * 400, SCREEN_CENTER[1] + 200), COLORS['pause_menu_button'], COLORS['pause_menu_button_hovered'], COLORS['pause_menu_button_shadow']))
        self.menu_heading_size = measure_text_ex(self.game.fonts['menu_heading'], self.menu_name, FONT_SIZES['menu_heading'], 0)

    def update(self) -> None:
        self.draw()
        if not self.clickable_entities:
            return

        # Only apply modulo when an item is active
        if self.hover_id != -1:
            self.hover_id = self.hover_id % len(self.clickable_entities)

        # update hovers
        for i, entity in enumerate(self.clickable_entities):
            entity.controller_hovered = (i == self.hover_id)
            entity.update()
            if entity.clicked:
                entity.clicked = False
                match entity.text:
                    case "Quit": 
                        self.game.save_game_data()
                        self.game.running = False
                    case "No":
                        self.game.current_menu_tab = MenuTab(self.game, "Settings")
                    case "Back":
                        if self.menu_name == "Audio":
                            set_music_volume(self.game.current_track, MUSIC_VOLUMES[cast(str, self.game.current_key)] * self.game.master_volume * MUSIC_PAUSE_DIM_FACTOR)
                        self.game.current_menu_tab = MenuTab(self.game, "Settings")
                    case "Audio":
                        set_music_volume(self.game.current_track, MUSIC_VOLUMES[cast(str, self.game.current_key)] * self.game.master_volume)
                        self.game.current_menu_tab = MenuTab(self.game, entity.text)
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
        draw_texture(self.game.ui_images['menu_card'], 0, 0, WHITE)

        draw_text_ex(self.game.fonts['menu_heading'], self.menu_name, Vector2(SCREEN_CENTER[0] - self.menu_heading_size.x/2, SCREEN_CENTER[1] - 325), FONT_SIZES['menu_heading'], 0, COLORS['pause_menu_heading'])
        if self.menu_name in self.game.main_menu_tab_names:
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

        for text in self.static_texts:
            text.draw()
