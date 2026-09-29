from imports import *

# --- GENERAL ---
GAME_NAME: str = "Scattershell Isle"
TARGET_FPS: Annotated[int, (10-240)] = 60
TILE_SIZE: int = 64
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
SCREEN_CENTER: tuple[int, int] = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
CAMERA_ZOOM: float = 1.0
START_IN_FULLSCREEN: bool = False
HIDE_CURSOR_IN_FULLSCREEN: bool = False
INPUT_COOLDOWN_AFTER_SWITCHING_GAME_MODE: float = 0.1
MIN_BOOT_DURATION: float = 3.0

# --- GAMEPLAY ---
ENTITY_DATA: dict[str, dict[str, int|float]] = {
    'player': {'max_health': 12, 'speed': 200, 'damage': 15, 'attack_cooldown': 0.25, 'knockback': 3, 'knockback_speed': 200, 'hitbox_offset_v': 15, 'hitbox_offset_h': 3},
    'bamboo': {'max_health': 50, 'speed': 110, 'damage': 4, 'attack_cooldown': 0.3, 'knockback': 5, 'knockback_speed': 150, 'hitbox_offset_v': 0, 'hitbox_offset_h': 0, 'attack_speed': 200, 'notice_radius': 280, 'attack_radius': 100},
    'spirit': {'max_health': 50, 'speed': 125, 'damage': 1, 'attack_cooldown': 0.0, 'knockback': 6, 'knockback_speed': 180, 'hitbox_offset_v': 7, 'hitbox_offset_h': 8, 'attack_speed': 200, 'notice_radius': 280, 'attack_radius': 100},
    'squid': {'max_health': 50, 'speed': 110, 'damage': 2, 'attack_cooldown': 0.3, 'knockback': 4, 'knockback_speed': 150, 'hitbox_offset_v': 0, 'hitbox_offset_h': 0, 'attack_speed': 200, 'notice_radius': 280, 'attack_radius': 100},
    'raccoon': {'max_health': 100, 'speed': 110, 'damage': 2, 'attack_cooldown': 0.4, 'knockback': 1, 'knockback_speed': 130, 'hitbox_offset_v': 70, 'hitbox_offset_h': 60, 'attack_speed': 200, 'notice_radius': 450, 'attack_radius': 160},
}


HURT_TIMES: dict[str, float] = {
    'Player': 1.2,
    'Enemy': ENTITY_DATA['player']['attack_cooldown']
}

KNOCKBACK_TIMES: dict[str, float] = {
    'Player': 0.05,
    'Enemy': 0.15
}

# --- GRAPHICS ---
COLORS: dict[str, Color] = {
    'boot_screen_background': BLACK,
    'loading_bar_outline': GRAY,
    'loading_bar_filling': WHITE,
    'loading_bar_text': WHITE,
    'title_text': Color(10, 70, 255, 255),
    'title_text_shadow': RAYWHITE,
    'title_menu_button': Color(10, 70, 255, 255),
    'title_menu_button_hovered': RED,
    'title_menu_button_shadow': WHITE,
    'save_slot_rects': Color(0, 150, 255, 255),
    'save_slot_rects_hovered': RED,
    'save_slot_rects_outline': BLACK,
    'save_slot_info': DARKGRAY,
    'save_slot_main_info': BLACK,
    'save_slot_new_game': BLACK,
    'pause_menu_background': Color(174, 203, 255, 220),
    'pause_menu_heading': Color(10, 70, 255, 255),
    'pause_menu_button': Color(0, 150, 255, 255),
    'pause_menu_button_hovered': RED,
    'pause_menu_button_shadow': BLACK,
    'game_over_background': Color(200, 0, 0, 255),
    'game_over_text': BLACK,
    'game_over_text_shadow': DARKPURPLE,
    'game_over_hint': BLACK,
    'save_and_quit_prompt': BLACK,
    'master_volume_rect': RAYWHITE,
    'master_volume_rect_hovered': Color(252, 96, 96, 255),
    'master_volume_rect_outline': Color(144, 87, 52, 255),
    'master_volume_line': BLACK,
    'keyboard_bindings_note': Color(10, 70, 255, 255),
    'keyboard_bindings_prompt': PURPLE,
}

# Animations
PLAYER_ANIMATION_SPEED: float = 0.025
ENEMY_ANIMATION_SPEED: float = 0.05
GRASS_PARTICLES_ANIMATION_SPEED: float = 14.0
DEATH_ANIMATION_SPEED: float = 15.0
ATTACK_ANIMATION_SPEED: float = 14.0

HURT_FLICKER_FREQUENCY: float = 70.0

GRASS_PARTICLE_OFFSET: float = 50.0

DEFAULT_SWIPE_TO_BLACK_DURATION: float = 1.0
DEATH_SWITPE_TO_BLACK_DURATION: float = 1.7
DEFAULT_FADE_TO_BLACK_DURATION: float = 0.5
DEFAULT_FADE_FROM_BLACK_DURATION: float = 0.5
FADE_FROM_BLACK_AFTER_MENU_DURATION: float = 1.3

# Fonts
FONT_SIZES: dict[str, int] = {
    'loading_bar_text': 20,
    'title': 105,
    'title_menu_clickable_text': 80,
    'game_over': 105,
    'game_over_hint': 32,
    'menu_heading': 80,
    'settings_tab_clickable_text': 60,
    'save_and_quit_prompt': 70,
    'master_volume': 70,
    'keyboard_bindings_prompt': 70,
    'keyboard_bindings_note': 40,
    'save_slot_title': 30,
    'save_slot_info': 26,
    'save_slot_new_game': 45
}

MENU_BUTTON_HOVER_SIZE_INCREASE: int = 7

# --- AUDIO ---
MASTER_VOLUME: Annotated[float, (0-1)] = 1
MUSIC_PAUSE_DIM_FACTOR: Annotated[float, (0-1)] = 0.2
LOW_HEALTH_SFX_RETRIGGER_DURATION: Annotated[float, (0.5-4.0)] = 1.5

MUSIC_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'title': 1.0,
    'start_area': 1.0,
    'cave': 1.0,
}

SFX_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'loading_finished': 1.0,
    'transition': 1.0,
    'sword': 1.0,
    'grass_cut': 1.0,
    'enemy_hurt': 1.0,
    'player_hurt': 1.0,
    'title_click': 1.0,
    'menu_button_pressed': 1.0,
    'pause_menu_opened': 1.0,
    'menu_button_hovered': 1.0,
    'heart_collect': 1.0,
    'low_health': 0.6,
    'game_over': 1.0,
}

# pitch variations
PITCH_VARIATION_SWORD: float = 0.2
PITCH_VARIATION_ENEMY_HURT: float = 0.2
PITCH_VARIATION_PLAYER_HURT: float = 0.2
PITCH_VARIATION_GRASS_CUT: float = 0.2

# --- INPUT ---
KEY_TO_NAME: dict[int, str] = {val: var_name.replace('KEY_', '').replace("_", " ").title() 
                               for var_name, val in list(globals().items())
                               if var_name.startswith('KEY_') and isinstance(val, int)}# key to string conversion

DEFAULT_KEYBOARD_BINDINGS: dict[str, int] = {
                            'move_left': KEY_A,
                            'move_right': KEY_D,
                            'move_up': KEY_W,
                            'move_down': KEY_S,
                            'item_slot_1': KEY_ENTER,
                            'item_slot_2': KEY_SPACE,
                            'open_inventory': KEY_TAB,
                            'open_map': KEY_M,
                            'menu_move_left': KEY_LEFT,# non-remappable
                            'menu_move_right': KEY_RIGHT, # non-remappable
                            'menu_move_up': KEY_UP, # non-remappable
                            'menu_move_down': KEY_DOWN, # non-remappable                      
                            'switch_menu_tab_right': KEY_E, # non-remappable
                            'switch_menu_tab_left': KEY_Q, # non-remappable
                            'confirm': KEY_ENTER, # non-remappable
                            'menu_back': KEY_ESCAPE, # non-remappable
                            'fullscreen': KEY_F11} # keyboard only

REMAPPABLE_ACTIONS: Set[str] = {'move_left', 'move_right', 'move_up', 'move_down', 'item_slot_1', 'item_slot_2', 'open_inventory', 'open_map'}
NON_REMAPPABLE_KEYS: Set[int] = {DEFAULT_KEYBOARD_BINDINGS['fullscreen'], KEY_RIGHT_SUPER, KEY_LEFT_SUPER}
NON_MAPPABLE_KEYS_TO_PAUSE: Set[int] = {DEFAULT_KEYBOARD_BINDINGS[key] for key in ('fullscreen', 'menu_move_left', 'menu_move_right', 'menu_move_up', 'menu_move_down', 'switch_menu_tab_right', 'switch_menu_tab_left')}

CONTROLLER_BINDINGS: dict[str, int] = {
                            'move_left': GAMEPAD_BUTTON_LEFT_FACE_LEFT,
                            'move_right': GAMEPAD_BUTTON_LEFT_FACE_RIGHT,
                            'move_up': GAMEPAD_BUTTON_LEFT_FACE_UP,
                            'move_down': GAMEPAD_BUTTON_LEFT_FACE_DOWN,
                            'item_slot_1': GAMEPAD_BUTTON_RIGHT_FACE_DOWN,
                            'item_slot_2': GAMEPAD_BUTTON_RIGHT_FACE_RIGHT,
                            'open_inventory': GAMEPAD_BUTTON_MIDDLE_RIGHT,
                            'open_map': GAMEPAD_BUTTON_MIDDLE_LEFT,
                            'switch_menu_tab_right': GAMEPAD_BUTTON_RIGHT_TRIGGER_1,
                            'switch_menu_tab_left': GAMEPAD_BUTTON_LEFT_TRIGGER_1,
                            'menu_move_left': GAMEPAD_BUTTON_LEFT_FACE_LEFT,
                            'menu_move_right': GAMEPAD_BUTTON_LEFT_FACE_RIGHT,
                            'menu_move_up': GAMEPAD_BUTTON_LEFT_FACE_UP,
                            'menu_move_down': GAMEPAD_BUTTON_LEFT_FACE_DOWN,                            
                            'confirm': GAMEPAD_BUTTON_RIGHT_FACE_RIGHT,
                            'menu_back': GAMEPAD_BUTTON_RIGHT_FACE_DOWN}

CONTROLLER_DEAD_ZONE: Annotated[float, (0.0-1.0)] = 0.25
