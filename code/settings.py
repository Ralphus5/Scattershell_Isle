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

# --- GAMEPLAY ---
PLAYER_HITBOX_OFFSET: int = 15
PLAYER_SPEED: int = 350

# --- GRAPHICS ---
COLORS: dict[str, Color] = {
    'pause_menu_tint': Color(30,30,30,150),
}

# --- AUDIO ---
# user volume settings
MASTER_VOLUME: Annotated[float, (0-1)] = 1

MUSIC_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'title': 1.0,
    'overworld': 1.0,
    'cave': 1.0,
}

SFX_VOLUMES: dict[str, Annotated[float, (0.0-1.0)]] = {
    'transition': 1.0,
}

# --- INPUT ---
NON_REMAPPABLE_ACTIONS: Set[str] = {'toggle_fullscreen', 'pause'}

DEFAULT_KEYBOARD_BINDINGS: dict[str, int] = {
                            'move_left': KEY_A,
                            'move_right': KEY_D,
                            'move_up': KEY_W,
                            'move_down': KEY_S,
                            'pause': KEY_ESCAPE,
                            'fullscreen': KEY_F11} # keyboard only

DEFAULT_CONTROLLER_BINDINGS: dict[str, int] = {
                            'move_left': GAMEPAD_BUTTON_LEFT_FACE_LEFT,
                            'move_right': GAMEPAD_BUTTON_LEFT_FACE_RIGHT,
                            'move_up': GAMEPAD_BUTTON_LEFT_FACE_UP,
                            'move_down': GAMEPAD_BUTTON_LEFT_FACE_DOWN,
                            'pause': GAMEPAD_BUTTON_MIDDLE_RIGHT,
}

CONTROLLER_DEAD_ZONE: Annotated[float, (0.0-1.0)] = 0.25
