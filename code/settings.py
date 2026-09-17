from imports import *

# --- GENERAL ---
GAME_NAME: str = "Scattershell Isle"
TARGET_FPS: Annotated[int, (30-240)] = 60
TILE_SIZE: int = 64
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
SCREEN_CENTER: tuple[int, int] = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
CAMERA_ZOOM: float = 1.0
START_IN_FULLSCREEN: bool = False
INPUT_COOLDOWN_AFTER_SWITCHING_GAME_MODE: float = 0.1

# --- GAMEPLAY ---
ENTITY_DATA: dict[str, dict[str, int|float]] = {
    'player': {'health': 100, 'speed': 230, 'damage': 15, 'attack_cooldown': 0.25, 'knockback': 4, 'hitbox_offset_v': 15, 'hitbox_offset_h': 3},
    'bamboo': {'health': 50, 'speed': 120, 'damage': 20, 'attack_cooldown': 0.1, 'knockback': 5, 'hitbox_offset_v': 0, 'hitbox_offset_h': 0, 'attack_speed': 200, 'notice_radius': 300, 'attack_radius': 90},
    'spirit': {'health': 50, 'speed': 130, 'damage': 20, 'attack_cooldown': 0, 'knockback': 5, 'hitbox_offset_v': 7, 'hitbox_offset_h': 8, 'attack_speed': 200, 'notice_radius': 300, 'attack_radius': 90},
    'squid': {'health': 50, 'speed': 120, 'damage': 20, 'attack_cooldown': 0.1, 'knockback': 5, 'hitbox_offset_v': 0, 'hitbox_offset_h': 0, 'attack_speed': 200, 'notice_radius': 300, 'attack_radius': 90},
    'raccoon': {'health': 50, 'speed': 120, 'damage': 20, 'attack_cooldown': 0.4, 'knockback': 1, 'hitbox_offset_v': 70, 'hitbox_offset_h': 60, 'attack_speed': 200, 'notice_radius': 500, 'attack_radius': 160},
}

# animations
HURT_TIMES: dict[str, float] = {
    'Player': 1.2,
    'Enemy': ENTITY_DATA['player']['attack_cooldown']
}

KNOCKBACK_TIMES: dict[str, float] = {
    'Player': 0.05,
    'Enemy': 0.2
}

PLAYER_ANIMATION_SPEED: float = 0.025
ENEMY_ANIMATION_SPEED: float = 0.05

# --- GRAPHICS ---
COLORS: dict[str, Color] = {
    'title_text': Color(10,70,255,255),
    'title_text_shadow': WHITE,
    'pause_menu_background': Color(174,203,255,220),
    'pause_menu_heading': Color(10,70,255,255),
    'pause_menu_button': Color(10,70,255,255),
    'pause_menu_button_hovered': RED,
    'game_over_text': RED,
    'game_over_text_shadow': DARKPURPLE,
    'save_and_quit_prompt': BLACK,
    'master_volume': Color(10,70,255,255),
    'master_volume_rect': RAYWHITE,
    'master_volume_rect_hovered': Color(252,96,96,255),
    'master_volume_rect_outline': Color(144,87,52,255),
    'master_volume_line': BLACK
}

 # fonts
FONT_SIZES: dict[str, int] = {
    'title': 105,
    'game_over': 105,
    'menu_heading': 80,
    'settings_tab_clickable_text': 60,
    'save_and_quit_prompt': 65,
    'master_volume': 70,
    'debugging': 30,
}

# --- AUDIO ---
# user volume settings
MASTER_VOLUME: Annotated[float, (0-1)] = 1
MUSIC_PAUSE_DIM_FACTOR: Annotated[float, (0-1)] = 0.2

MUSIC_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'title': 1.0,
    'start_area': 1.0,
    'cave': 1.0,
}

SFX_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'transition': 1.0,
    'sword': 1.0,
    'grass_cut': 1.0,
    'enemy_hurt': 1.0,
    'player_hurt': 1.0,
    'menu_button_pressed': 1.0,
    'pause_menu_opened': 1.0,
    'menu_button_hovered': 1.0,
}

# pitch variations
PITCH_VARIATION_SWORD: float = 0.2
PITCH_VARIATION_ENEMY_HURT: float = 0.2
PITCH_VARIATION_PLAYER_HURT: float = 0.2
PITCH_VARIATION_GRASS_CUT: float = 0.2

# --- INPUT ---
NON_REMAPPABLE_ACTIONS: Set[str] = {'toggle_fullscreen', 'controller_menu_back', 'open_inventory', 'open_map', 'switch_menu_tab_right', 'switch_menu_tab_left', 'menu_move_left', 'menu_move_right', 'menu_move_up', 'menu_move_down', 'confirm'}

DEFAULT_KEYBOARD_BINDINGS: dict[str, int] = {
                            'move_left': KEY_A,
                            'move_right': KEY_D,
                            'move_up': KEY_W,
                            'move_down': KEY_S,
                            'menu_move_left': KEY_LEFT,
                            'menu_move_right': KEY_RIGHT,
                            'menu_move_up': KEY_UP,
                            'menu_move_down': KEY_DOWN,
                            'item_slot_1': KEY_ENTER,
                            'item_slot_2': KEY_SPACE,
                            'open_inventory': KEY_ESCAPE,
                            'open_map': KEY_BACKSPACE,
                            'switch_menu_tab_right': KEY_E,
                            'switch_menu_tab_left': KEY_Q,
                            'confirm': KEY_ENTER,
                            'fullscreen': KEY_F11} # keyboard only

DEFAULT_CONTROLLER_BINDINGS: dict[str, int] = {
                            'move_left': GAMEPAD_BUTTON_LEFT_FACE_LEFT,
                            'move_right': GAMEPAD_BUTTON_LEFT_FACE_RIGHT,
                            'move_up': GAMEPAD_BUTTON_LEFT_FACE_UP,
                            'move_down': GAMEPAD_BUTTON_LEFT_FACE_DOWN,
                            'menu_move_left': GAMEPAD_BUTTON_LEFT_FACE_LEFT,
                            'menu_move_right': GAMEPAD_BUTTON_LEFT_FACE_RIGHT,
                            'menu_move_up': GAMEPAD_BUTTON_LEFT_FACE_UP,
                            'menu_move_down': GAMEPAD_BUTTON_LEFT_FACE_DOWN,
                            'item_slot_1': GAMEPAD_BUTTON_RIGHT_FACE_DOWN,
                            'item_slot_2': GAMEPAD_BUTTON_RIGHT_FACE_RIGHT,
                            'open_inventory': GAMEPAD_BUTTON_MIDDLE_RIGHT,
                            'open_map': GAMEPAD_BUTTON_MIDDLE_LEFT,
                            'switch_menu_tab_right': GAMEPAD_BUTTON_RIGHT_TRIGGER_1,
                            'switch_menu_tab_left': GAMEPAD_BUTTON_LEFT_TRIGGER_1,
                            'confirm': GAMEPAD_BUTTON_RIGHT_FACE_RIGHT,
                            'controller_menu_back': GAMEPAD_BUTTON_RIGHT_FACE_DOWN} # controller only

CONTROLLER_DEAD_ZONE: Annotated[float, (0.0-1.0)] = 0.25
