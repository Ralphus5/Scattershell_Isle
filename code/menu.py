from player import *

class MenuTab:
    def __init__(self, game: Game, menu_name: str) -> None:
        self.game = game
        self.menu_name = menu_name
        self.clickable_entities: list[ClickableText] = []
        self.hover_id = -1
        match self.menu_name:
            case "Map": # map
                pass
                #self.clickable_entities.append() 
            case "Inventory": # inventory
                pass
                #self.clickable_entities.append() 
            case "Settings": # settings
                pass
                for text in enumerate(["Audio", "Controls", "QUIT & SAVE"]):
                    self.clickable_entities.append(ClickableText(game, text[1], game.fonts['settings_tab_clickable_text'], FONT_SIZES['settings_tab_clickable_text'], 0, (SCREEN_CENTER[0], (SCREEN_CENTER[1] - 190/2) + (text[0] * 140)), COLORS['pause_menu_button'], None, COLORS['pause_menu_button_hovered']))
            case "Save & Quit":
                pass 
        self.menu_heading_size = measure_text_ex(self.game.fonts['menu_heading'], self.menu_name, FONT_SIZES['menu_heading'], 0)

    def update(self, dt: float) -> None:
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
                self.game.current_menu_tab = MenuTab(self.game, entity.text)
            entity.draw()

    def draw(self) -> None:
        draw_texture(self.game.ui_images['menu_card'], 0, 0, WHITE)
        draw_text_ex(self.game.fonts['menu_heading'], self.menu_name, Vector2(SCREEN_CENTER[0] - self.menu_heading_size.x/2, SCREEN_CENTER[1] - 325), FONT_SIZES['menu_heading'], 0, COLORS['pause_menu_heading'])
        if self.menu_name in self.game.main_menu_tab_names:
            draw_triangle(Vector2(380,45), Vector2(330,70), Vector2(380,100), COLORS['pause_menu_button_hovered'] if self.game.input_down('switch_menu_tab_left') else COLORS['pause_menu_button'])
            draw_triangle(Vector2(900,45), Vector2(900,100), Vector2(950,70), COLORS['pause_menu_button_hovered'] if self.game.input_down('switch_menu_tab_right') else COLORS['pause_menu_button'])
