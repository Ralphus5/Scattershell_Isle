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
    draw_text_ex(font, info_text, Vector2(pos_x, pos_y), FONT_SIZES['debugging'], 1, WHITE)
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
        self.original_duration = self.duration
        self.use_play_time = use_play_time
        self.repeat = repeat
        self.callback = callback
        self.original_callback = self.callback
        self.start_time = 0.0
        self.active = False
        self.elapsed_time = 0.0

        if autostart:
            self.activate()

    @property
    def current_time(self) -> float:
        return self.game.play_time if self.use_play_time else self.game.runtime

    def activate(self, alternate_duration: Optional[float] = None, alternate_callback: Optional[Callable] = None) -> None:
        self.duration = alternate_duration if alternate_duration else self.original_duration
        self.callback = alternate_callback if alternate_callback else self.original_callback
        self.active = True
        self.start_time = self.current_time

    def deactivate(self) -> None:
        self.active = False
        self.elapsed_time = 0.0

    def update(self) -> None:
        if self.active:
            self.elapsed_time = self.current_time - self.start_time
            if self.elapsed_time >= self.duration:
                if self.callback:
                    self.callback()
                self.deactivate()
                if self.repeat:
                    self.activate(self.duration, self.callback)

class RegularText:
    def __init__(self, game: Game, text: str, font: Font, font_size: int, font_spacing: int, pos: tuple[float, float] | Vector2, color: Color, shadow_color: Optional[Color] = None) -> None:
        self.game = game
        self.font = font
        self.original_font_size = font_size
        self.font_size = font_size
        self.font_spacing = font_spacing
        self.text = text
        self.color = color
        self.shadow_color = shadow_color
        self.center = Vector2(pos[0], pos[1]) if isinstance(pos, tuple) else pos
        self.set_position_and_size()

    def set_position_and_size(self, new_font_size: Optional[int] = None, new_center: Optional[Vector2 | tuple[float, float]] = None) -> None:
        """Recalculates text dimensions for current self.text and recenters top-left self.pos around self.center."""
        if new_center is not None:
            self.center = Vector2(new_center[0], new_center[1]) if isinstance(new_center, tuple) else new_center

        self.font_size = new_font_size if new_font_size is not None else self.original_font_size
        self.text_size = measure_text_ex(self.font, self.text, self.font_size, self.font_spacing)
        
        # Top-left rendering position derived from center anchor and current text dimensions
        self.pos = vector2_subtract(self.center, vector2_multiply_value(self.text_size, 0.5))

    def draw_shadow(self) -> None:
        if self.shadow_color:
            draw_text_ex(self.font, self.text, vector2_add_value(self.pos, 2), self.font_size, 0, self.shadow_color)    

    def draw(self) -> None:
        self.draw_shadow()
        draw_text_ex(self.font, self.text, self.pos, self.font_size, 0, self.color)

class ClickableText(RegularText):

    def __init__(self, game: Game, text: str, font: Font, font_size: int, font_spacing: int, pos: tuple[float, float] | Vector2, color: Color, hover_color: Color, shadow_color: Optional[Color] = None) -> None:
        super().__init__(game, text, font, font_size, font_spacing, pos, color, shadow_color)
        self.hover_color = hover_color
        self.hovered = False
        self.clicked = False
        self.hover_changed = False
        self.controller_hovered = False

    def update(self) -> None:
        prev_hover = self.hovered
        self.hovered = self.controller_hovered
        self.hover_changed = (self.hovered != prev_hover)

        if self.hover_changed:  
            if self.hovered:
                self.set_position_and_size(self.original_font_size + MENU_BUTTON_HOVER_SIZE_INCREASE)
                self.game.play_sfx('menu_button_hovered')
            else:
                self.set_position_and_size()

        if self.clicked:
            self.game.play_sfx('menu_button_pressed')

    def draw(self) -> None:
        self.draw_shadow()
        current_color = self.hover_color if self.hovered else self.color
        draw_text_ex(self.font, self.text, self.pos, self.font_size, self.font_spacing, current_color)

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

def vector2_multiply_value(vector: Vector2, value: float) -> Vector2:
    return Vector2(vector.x * value, vector.y * value)

def inflate_rect(rect: Rectangle, width: float, height: float) -> Rectangle:
    """Vergrößert/Verkleinert ein Rectangle zentriert (wie rect.inflate in Pygame)"""
    return Rectangle(
        rect.x - width / 2,
        rect.y - height / 2,
        rect.width + width,
        rect.height + height)

def import_image_folder(path: str) -> list[Texture]:
    texture_list: list[Texture] = []
    with os.scandir(path) as entries:
        files = sorted([e.path for e in entries if e.is_file() and e.name.endswith('.png')])
        for full_path in files:
            texture_list.append(load_texture(full_path))
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
