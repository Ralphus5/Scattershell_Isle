from settings import *

# --- Debug and Tools ---

def debug(game: Game, font: Font, info, pos_x: int = 10, pos_y: int = 10) -> None:
    """Draws a variable as text on the virtual screen"""
    info_text = str(info)
    font_size = 40
    width = measure_text(info_text, font_size)
    rectangle = Rectangle(pos_x - 10,pos_y - 10, width, font_size + 20)
    begin_texture_mode(game.virtual_screen)
    draw_rectangle_rec(rectangle, BLACK)
    draw_text_ex(font, info_text, Vector2(pos_x,pos_y), font_size, 1, WHITE)
    end_texture_mode()

def draw_grid_2d(width: int, height: int, cell_size: int, color: Color = LIGHTGRAY):
    # vertical lines
    for x in range(0, width + 1, cell_size):
        draw_line(x, 0, x, height, color)
        
    # horizontal lines
    for y in range(0, height + 1, cell_size):
        draw_line(0, y, width, y, color)

def get_func_time(func: Callable) -> Callable:
    '''DEBUGGING TOOL: Check how long a function took to execute.'''

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time: float = perf_counter()
        result: Any = func(*args, **kwargs)
        end_time: float = perf_counter()

        print(f'"{func.__name__}()" took {end_time - start_time:.3f} seconds to execute')
        return result

    return wrapper

# --- Game Essentials ---

# input
def check_dead_zone(axis: float) -> int:
    if not abs(axis) > CONTROLLER_DEAD_ZONE:
        return 0
    if axis > 0:
        return 1
    else:
        return -1

def is_action_pressed(action: str) -> bool:
    key = KEYBOARD_BINDINGS.get(action)
    button = CONTROLLER_BINDINGS.get(action)

    if key is not None and is_key_pressed(key):
        return True
    if button is not None and is_gamepad_available(0) and is_gamepad_button_pressed(0, button):
        return True
    return False

def is_action_down(action: str) -> bool:
    key = KEYBOARD_BINDINGS.get(action)
    button = CONTROLLER_BINDINGS.get(action)

    if key is not None and is_key_down(key):
        return True
    if button is not None and is_gamepad_available(0) and is_gamepad_button_down(0, button):
        return True
    return False

# misc
def inflate_rect(rect: Rectangle, width: float, height: float) -> Rectangle:
    """Vergrößert/Verkleinert ein Rectangle zentriert (wie rect.inflate in Pygame)"""
    return Rectangle(
        rect.x - width / 2,
        rect.y - height / 2,
        rect.width + width,
        rect.height + height)

def import_image_folder(path: str) -> list[Texture]:
    texture_list: list[Texture] = []
    for _,__,image_files in os.walk(path):
        for image in image_files:
            full_path = join(path, image)
            texture = load_texture(full_path)
            texture_list.append(texture)
    return texture_list

@dataclass
class Circle:
    center: Vector2
    radius: float

    # Optional helper properties
    @property
    def x(self) -> float:
        return self.center.x

    @property
    def y(self) -> float:
        return self.center.y

# time system
def update_play_time(game: Game) -> None:
    if game.state == 'play':
        game.play_time = game.runtime - game.play_start - game.total_paused

def pause_play_time(game: Game) -> None:
    game.pause_start = game.runtime

def resume_play_time(game: Game) -> None:
    game.total_paused += game.runtime - game.pause_start

class Timer:
    def __init__(self, game: Game, duration: float, use_play_time: bool = True, autostart: bool = False, repeat: bool = False, callback: Optional[Callable] = None):
        self.game = game
        self.duration = duration
        self.use_play_time = use_play_time
        self.repeat = repeat
        self.callback = callback
        self.start_time = 0.0
        self.active = False

        if autostart:
            self.activate()

    @property
    def current_time(self) -> float:
        return self.game.play_time if self.use_play_time else self.game.runtime

    def activate(self) -> None:
        self.active = True
        self.start_time = self.current_time

    def deactivate(self) -> None:
        self.active = False

    def update(self) -> None:
        if self.active:
            if self.current_time - self.start_time >= self.duration:
                if self.callback:
                    self.callback()
                self.deactivate()
                if self.repeat:
                    self.activate()