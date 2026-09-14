from settings import *

# --- Debug and Tools ---

def debug(game: Game, font: Font, info, pos_x: int = 10, pos_y: int = 10) -> None:
    """Draws a variable as text on the virtual screen"""
    info_text = str(info)
    font_size = 30
    
    # Measure dimensions using the custom Raylib font
    text_size = measure_text_ex(font, info_text, font_size, 1)
    rectangle = Rectangle(pos_x - 10, pos_y - 10, text_size.x + 20, font_size + 20)
    
    begin_texture_mode(game.virtual_screen)
    draw_rectangle_rec(rectangle, BLACK)
    draw_text_ex(font, info_text, Vector2(pos_x, pos_y), font_size, REGULAR_FONT_SPACING, WHITE)
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

@dataclass
class Circle:
    center: Vector2
    radius: float

    @property
    def x(self) -> float:
        return self.center.x

    @property
    def y(self) -> float:
        return self.center.y

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

def load_file(file: str, process: str = '') -> dict:
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            msg = f"Failed to load {file}: {e}"
            if process:
                msg += f" -> {process} failed!"
            print(msg)
    return {}

def save_file(file: str, data: dict, process: str = '') -> bool:
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except (json.JSONDecodeError, OSError) as e:
        msg = f"Failed to save {file}: {e}"
        if process:
            msg += f" -> {process} failed!"
        print(msg)
        return False