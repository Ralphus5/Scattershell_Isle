from level import *

class StateManager:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.state = 'boot'
        self.requested_state = 'title'

    def change_game_mode(self) -> None:
        if not self.requested_state or self.requested_state == self.state:
            return
        # --- Change state ---
        old, new = self.state, self.requested_state
        self.requested_state = ''
        self.state = new

        # --- Drain input buffer after menu switching ---
        self.game.input_manager.input_cooldown_timer.activate()

        # --- TITLE ---
        if new == 'title':
            if old == 'boot':
                self.game.audio_manager.play_music('title')

        # --- PLAY ---
        elif new == 'play':
            if old == 'title':
                self.level = Level(self.game, self.game.last_saved_current_map)
                # set player position if saved
                self.game.time_manager.play_start = get_time()
            elif old == 'pause':
                self.game.time_manager.resume_play_time()
                self.game.audio_manager.resume_music()
            elif old == 'game_over':
                self.game.time_manager.resume_play_time()
                self.game.save_game_data()
                self.game.load_save_data()
                self.level = Level(self.game, self.game.last_saved_current_map)
                self.game.audio_manager.play_music(self.level.current_map, True)

        # --- PAUSE ---
        elif new == 'pause':
            if old == 'play':
                self.game.time_manager.pause_play_time()
                self.game.audio_manager.pause_music()

        # --- GAME OVER ---
        elif new == 'game_over':
            self.game.audio_manager.pause_music()
            self.game.time_manager.pause_play_time()

    def handle_game_mode(self, dt) -> None:
        if self.state == 'title':
            self.game.title_screen()
        elif self.state == 'play':
            self.level.run(dt)
        elif self.state == 'pause':
            self.game.pause_menu()
        elif self.state == 'game_over':
            self.game.game_over_screen()

class InputManager:
    def __init__(self, game: Game) -> None:
        self.game = game
        set_exit_key(0)
        self.input_cooldown_timer = Timer(self.game,INPUT_COOLDOWN_AFTER_SWITCHING_GAME_MODE, False, False,False)
        self.keyboard_bindings = dict(DEFAULT_KEYBOARD_BINDINGS)
        self.controller_bindings = dict(DEFAULT_CONTROLLER_BINDINGS)

    def get_general_input(self) -> None:
        self.input_cooldown_timer.update()
        # --- universal input ---
        if self.pressed('fullscreen'):
            toggle_fullscreen()
            hide_cursor() if is_window_fullscreen() else show_cursor()

        # --- TITLE ---
        if self.game.state_manager.state == 'title':
            if self.pressed('pause') or self.pressed('confirm'):
                self.game.state_manager.requested_state = 'play'

        # --- PLAY ---
        elif self.game.state_manager.state == 'play':
            if self.pressed('pause'):
                self.game.state_manager.requested_state = 'pause'

        # --- PAUSE ---
        elif self.game.state_manager.state == 'pause':
            if self.pressed('pause'):
                self.game.state_manager.requested_state = 'play'

        # --- GAME OVER ---
        elif self.game.state_manager.state == 'game_over':
            if self.pressed('confirm'):
                self.game.state_manager.requested_state = 'play'

    def load_user_bindings(self):
        data = load_file(self.game.SETTINGS_FILE, "Loading keybindings")
        if 'keybindings' in data:
            if 'keyboard' in data['keybindings']:
                self.keyboard_bindings.update(data['keybindings']['keyboard'])
            if 'controller' in data['keybindings']:
                self.controller_bindings.update(data['keybindings']['controller'])

    def save_user_bindings(self):
        current_process = "Saving keybindings"
        save_data = load_file(self.game.SETTINGS_FILE, current_process)

        current_kb = {k: v for k, v in self.keyboard_bindings.items() if k not in NON_REMAPPABLE_ACTIONS}
        current_ctrl = {k: v for k, v in self.controller_bindings.items() if k not in NON_REMAPPABLE_ACTIONS}

        save_data['keybindings'] = {
                    'keyboard': current_kb,
                    'controller': current_ctrl
                }

        save_file(self.game.SETTINGS_FILE, save_data, current_process)

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
        if self.input_cooldown_timer.active:
            return False
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

    def play_music(self, key: str, restart: bool = False) -> None:
        stripped_key = key.strip('0123456789')
        if self.current_key == stripped_key and not restart:
            return  # Already playing this track!

        if self.current_track:
            stop_music_stream(self.current_track)

        if stripped_key in self.game.music:
            self.current_key = stripped_key
            self.current_track = self.game.music[stripped_key]
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