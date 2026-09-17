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
    draw_text_ex(font, info_text, Vector2(pos_x, pos_y), font_size, FONT_SIZES['debugging'], WHITE)
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

class RegularText:
    def __init__(self, game: Game, text: str, font: Font, font_size: int, font_spacing: int, pos: tuple[float, float], color: Color, shadow_color: Optional[Color]) -> None:
        self.game = game
        self.font = font
        self.font_size = font_size
        self.font_spacing = font_spacing
        self.text = text
        self.color = color
        self.text_size = measure_text_ex(self.font, self.text, self.font_size, self.font_spacing)
        self.pos = Vector2(pos[0] - self.text_size.x/2, pos[1] - self.text_size.y/2)
        self.shadow_color = shadow_color

    def draw_shadow(self) -> None:
        if self.shadow_color:
            draw_text_ex(self.font, self.text, Vector2(self.pos.x + 2, self.pos.y + 2), self.font_size, 0, self.shadow_color)    

    def draw(self):
        self.draw_shadow()
        draw_text_ex(self.font, self.text, self.pos, self.font_size, 0, self.color)

class ClickableText(RegularText):
    """Clickable text button that changes color when hovered."""

    def __init__(self, game: Game, text: str, font: Font, font_size: int, font_spacing: int, pos: tuple[float, float], color: Color, shadow_color: Optional[Color], hover_color: Color) -> None:
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

        if self.hover_changed and self.hovered:
            self.game.play_sfx('menu_button_hovered')

        if self.clicked:
            self.game.play_sfx('menu_button_pressed')

    def draw(self):
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