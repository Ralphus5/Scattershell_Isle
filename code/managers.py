from level import *

class StateManager:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.state = 'boot'
        self.requested_state = 'title'

    def change_game_mode(self) -> None:
        if not self.requested_state or self.requested_state == self.state:
            return
        old, new = self.state, self.requested_state
        self.requested_state = ''
        self.state = new

        # --- title ---
        if new == 'title':
            if old == 'boot':
                self.game.audio_manager.play_music('title')

        elif new == 'play':
            if old == 'title':
                self.level = Level(self.game)
                self.game.time_manager.play_start = get_time()
            elif old == 'pause':
                self.game.time_manager.resume_play_time()
                self.game.audio_manager.resume_music()

        elif new == 'pause':
            if old == 'play':
                self.game.time_manager.pause_play_time()
                self.game.audio_manager.pause_music()

    def handle_game_mode(self, dt) -> None:
        if self.state == 'title':
            self.game.title_screen()
        elif self.state == 'play':
            self.level.run(dt)
        elif self.state == 'pause':
            self.game.pause_menu()

class InputManager:
    def __init__(self, game: Game) -> None:
        self.game = game
        set_exit_key(0)
        self.keyboard_bindings = dict(DEFAULT_KEYBOARD_BINDINGS)
        self.controller_bindings = dict(DEFAULT_CONTROLLER_BINDINGS)

    def get_general_input(self) -> None:
        # --- universal input ---
        if self.pressed('fullscreen'):
            toggle_fullscreen()
            hide_cursor() if is_window_fullscreen() else show_cursor()

        # --- title ---
        if self.game.state_manager.state == 'title':
            if self.pressed('pause') or is_key_pressed(KEY_ENTER):
                self.game.state_manager.requested_state = 'play'

        # --- play ---
        elif self.game.state_manager.state == 'play':
            if self.pressed('pause'):
                self.game.state_manager.requested_state = 'pause'

        # --- pause ---
        elif self.game.state_manager.state == 'pause':
            if self.pressed('pause'):
                self.game.state_manager.requested_state = 'play'

    def load_user_bindings(self):
        if not os.path.exists(self.game.SETTINGS_FILE):
            return

        try:
            with open(self.game.SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                if 'keyboard' in data['keybindings']:
                    self.keyboard_bindings.update(data['keybindings']['keyboard'])
                if 'controller' in data['keybindings']:
                    self.controller_bindings.update(data['keybindings']['controller'])
        except (json.JSONDecodeError, OSError):
            print('Loading Keybindings failed!')

    def save_user_bindings(self):
        current_kb = {k: v for k, v in self.keyboard_bindings.items() if k not in NON_REMAPPABLE_ACTIONS}
        current_ctrl = {k: v for k, v in self.controller_bindings.items() if k not in NON_REMAPPABLE_ACTIONS}

        data = {'keybindings':
                {
                    'keyboard': current_kb,
                    'controller': current_ctrl
                }
                }
        try:
            with open(self.game.SETTINGS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except (json.JSONDecodeError, OSError):
            print('Saving keybindings failed!')

    def check_joystick_dead_zone(self, axis: float) -> int:
        if not abs(axis) > CONTROLLER_DEAD_ZONE:
            return 0
        if axis > 0:
            return 1
        else:
            return -1

    def get_player_movement_input(self) -> Vector2:
        direction_x = int(self.down('move_right')) - int(self.down('move_left'))
        direction_y = int(self.down('move_down')) - int(self.down('move_up'))

        # stick
        if is_gamepad_available(0):
            stick_x = self.check_joystick_dead_zone(get_gamepad_axis_movement(0, GAMEPAD_AXIS_LEFT_X))
            stick_y = self.check_joystick_dead_zone(get_gamepad_axis_movement(0, GAMEPAD_AXIS_LEFT_Y))
            # check for controller movement
            if any((stick_x,stick_y)):
                direction_x = stick_x
                direction_y = stick_y

        return Vector2(direction_x, direction_y)

    def pressed(self, action: str) -> bool:
        key = self.keyboard_bindings.get(action)
        button = self.controller_bindings.get(action)

        if key is not None and is_key_pressed(key):
            return True
        if button is not None and is_gamepad_available(0) and is_gamepad_button_pressed(0, button):
            return True
        return False

    def down(self, action: str) -> bool:
        key = self.keyboard_bindings.get(action)
        button = self.controller_bindings.get(action)

        if key is not None and is_key_down(key):
            return True
        if button is not None and is_gamepad_available(0) and is_gamepad_button_down(0, button):
            return True
        return False

class TimeManager:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.play_time = 0.0
        self.play_start = 0.0
        self.pause_start = 0.0
        self.total_paused = 0.0

    @property
    def runtime(self) -> float:
        return get_time()

    def update_play_time(self) -> None:
        if self.game.state_manager.state == 'play':
            self.play_time = self.runtime - self.play_start - self.total_paused

    def pause_play_time(self) -> None:
        self.pause_start = self.runtime

    def resume_play_time(self) -> None:
        self.total_paused += self.runtime - self.pause_start

class AudioManager:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.set_volumes()
        self.current_key: Optional[str] = None
        self.current_track: Music = self.game.music['title']

    def play_music(self, key: str) -> None:
        if self.current_key == key:
            return  # Already playing this track!

        if self.current_track:
            stop_music_stream(self.current_track)

        if key in self.game.music:
            self.current_key = key
            self.current_track = self.game.music[key]
            play_music_stream(self.current_track)

    def pause_music(self) -> None:
        if self.current_track:
            pause_music_stream(self.current_track)

    def resume_music(self) -> None:
        if self.current_track:
            resume_music_stream(self.current_track)

    def play_sfx(self, key: str, pitch_variation: float = 0.0) -> None:
            if key in self.game.sfx:
                sound = self.game.sfx[key]
                if pitch_variation > 0:
                    var = get_random_value(-int(pitch_variation * 100), int(pitch_variation * 100)) / 100.0
                    set_sound_pitch(sound, 1.0 + var)
                play_sound(sound)

    def update(self) -> None:
        if self.current_track: update_music_stream(self.current_track)

    def set_volumes(self) -> None:
        # --- music volumes ---
        for track in MUSIC_VOLUMES.keys():
            set_music_volume(self.game.music[track], MUSIC_VOLUMES[track] * MASTER_VOLUME)

        # --- sfx volumes ---
        for sound in SFX_VOLUMES.keys():
            set_sound_volume(self.game.sfx[sound], SFX_VOLUMES[sound] * MASTER_VOLUME)