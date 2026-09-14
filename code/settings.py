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
PLAYER_HITBOX_OFFSET_VERTICAL: int = 15
PLAYER_HITBOX_OFFSET_HORIZONTAL: int = 3
PLAYER_SPEED: int = 250
PLAYER_ATTACK_COOLDOWN: float = 0.25

# --- GRAPHICS ---
COLORS: dict[str, Color] = {
    'title_text': Color(10,70,255,255),
    'title_text_shadow': WHITE,
    'pause_menu_tint': Color(30,30,30,150),
}
 # fonts
TITLE_FONT_SPACING: int = 0
REGULAR_FONT_SPACING: int = 1
TITLE_FONT_SIZE: int = 105
REGULAR_FONT_SIZE: int = 30

# animations
PLAYER_ANIMATION_SPEED: float = 0.25 * PLAYER_SPEED/10

# --- AUDIO ---
# user volume settings
MASTER_VOLUME: Annotated[float, (0-1)] = 1

MUSIC_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'title': 1.0,
    'start_area': 1.0,
    'cave': 1.0,
}

SFX_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'transition': 1.0,
    'sword': 1.0,
}

# --- INPUT ---
NON_REMAPPABLE_ACTIONS: Set[str] = {'toggle_fullscreen', 'pause', 'confirm'}

DEFAULT_KEYBOARD_BINDINGS: dict[str, int] = {
                            'move_left': KEY_A,
                            'move_right': KEY_D,
                            'move_up': KEY_W,
                            'move_down': KEY_S,
                            'attack': KEY_ENTER,
                            'confirm': KEY_ENTER,
                            'pause': KEY_ESCAPE,
                            'fullscreen': KEY_F11} # keyboard only

DEFAULT_CONTROLLER_BINDINGS: dict[str, int] = {
                            'move_left': GAMEPAD_BUTTON_LEFT_FACE_LEFT,
                            'move_right': GAMEPAD_BUTTON_LEFT_FACE_RIGHT,
                            'move_up': GAMEPAD_BUTTON_LEFT_FACE_UP,
                            'move_down': GAMEPAD_BUTTON_LEFT_FACE_DOWN,
                            'attack': GAMEPAD_BUTTON_RIGHT_FACE_DOWN,
                            'confirm': GAMEPAD_BUTTON_RIGHT_FACE_DOWN,
                            'pause': GAMEPAD_BUTTON_MIDDLE_RIGHT,
}

CONTROLLER_DEAD_ZONE: Annotated[float, (0.0-1.0)] = 0.25
