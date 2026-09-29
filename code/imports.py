"""Explicit imports are done for functions that are actually used. Expections are os, sys, json and re, 
where objects are prefixed. For datetime, one should mind, that it contains datetime.datetime!
In addition, every module is imported for auto-completion look-ups."""

import pyray
from pyray import (Image, Texture, Vector2, Color, WHITE, BLACK, RED, GRAY, RAYWHITE, PURPLE, DARKPURPLE, DARKGRAY, LIGHTGRAY, BLUE, GREEN,
                   Rectangle, Font, Sound, Music, Camera2D, draw_texture_ex, draw_line, draw_text_ex, draw_rectangle_lines, draw_rectangle_rec, 
                   begin_texture_mode, end_texture_mode, begin_drawing, end_drawing, begin_mode_2d, end_mode_2d, load_texture, 
                   set_music_volume, measure_text_ex, draw_texture_pro, vector2_add, vector2_subtract, vector2_length, 
                   vector2_normalize, clamp, check_collision_recs, check_collision_circle_rec, vector2_negate, 
                   clear_background, draw_texture, set_exit_key, window_should_close, get_frame_time, update_music_stream,
                   toggle_fullscreen, hide_cursor, is_window_fullscreen, show_cursor, is_key_down, is_key_pressed, get_time,
                   draw_rectangle_lines_ex, draw_rectangle, get_screen_height, get_screen_width, init_window, init_audio_device,
                   set_target_fps, load_render_texture, load_image, set_window_icon, load_font_ex, ffi, load_sound,
                   load_music_stream, is_gamepad_available, get_gamepad_axis_movement, is_gamepad_button_down, is_gamepad_button_pressed,
                   stop_music_stream, play_music_stream, pause_music_stream, resume_music_stream, get_random_value, set_sound_pitch,
                   play_sound, set_sound_volume, close_audio_device, close_window, draw_triangle, draw_line_ex, vector2_add_value,
                   draw_circle_lines_v, gui_check_box, gui_button, set_mouse_offset, set_mouse_scale, is_mouse_button_pressed, check_collision_point_rec,
                   is_mouse_button_released, get_mouse_position, gui_slider, gui_window_box, gui_group_box, gui_label, get_font_default, get_fps,
                   gui_combo_box, load_shader, get_shader_location, set_shader_value, begin_shader_mode, end_shader_mode, set_shader_value_v,
                   set_shader_value_texture, begin_blend_mode, get_world_to_screen_2d, draw_circle_gradient, end_blend_mode, draw_texture_rec) 
import pytmx
from pytmx import TiledMap
import pymunk
import typing
from typing import (Annotated, Any, Set, Callable, Optional, Generator, TYPE_CHECKING, cast)
import math
from math import sin
import random
from random import choice, uniform
import time
from time import perf_counter
from datetime import timedelta, datetime
import dataclasses
from dataclasses import dataclass
import functools
from functools import wraps
import operator
from operator import attrgetter
import os
import os.path
from os.path import join
import sys
import json
import re

# --- Raylib Keys and Buttons ---
import raylib
from raylib import (KEY_A, KEY_D, KEY_S, KEY_W, KEY_Q, KEY_E, KEY_R, KEY_T, KEY_Z, KEY_U, KEY_I,
KEY_O, KEY_P, KEY_F, KEY_G, KEY_H, KEY_J, KEY_K, KEY_L, KEY_Y, KEY_X, KEY_C, KEY_V, KEY_B, KEY_N,
KEY_M, KEY_LEFT_SHIFT, KEY_RIGHT_SHIFT, KEY_BACK, KEY_ENTER, KEY_SPACE, KEY_ESCAPE, KEY_TAB, KEY_F3,
KEY_F11, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_BACKSPACE, KEY_RIGHT_SUPER, KEY_LEFT_SUPER)

from raylib import (GAMEPAD_AXIS_LEFT_X, GAMEPAD_AXIS_LEFT_Y, GAMEPAD_AXIS_RIGHT_X, GAMEPAD_AXIS_RIGHT_Y,
GAMEPAD_BUTTON_LEFT_FACE_DOWN, GAMEPAD_BUTTON_LEFT_FACE_LEFT, GAMEPAD_BUTTON_LEFT_FACE_RIGHT, GAMEPAD_BUTTON_LEFT_FACE_UP,
GAMEPAD_BUTTON_MIDDLE_RIGHT, GAMEPAD_BUTTON_MIDDLE_LEFT, GAMEPAD_BUTTON_MIDDLE, GAMEPAD_BUTTON_LEFT_TRIGGER_1,
GAMEPAD_BUTTON_LEFT_TRIGGER_2, GAMEPAD_BUTTON_RIGHT_TRIGGER_1, GAMEPAD_BUTTON_RIGHT_TRIGGER_2, GAMEPAD_BUTTON_RIGHT_FACE_DOWN,
GAMEPAD_BUTTON_RIGHT_FACE_UP, GAMEPAD_BUTTON_RIGHT_FACE_LEFT, GAMEPAD_BUTTON_RIGHT_FACE_RIGHT)

from raylib import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_MIDDLE

# --- Shaders ---
from raylib import SHADER_UNIFORM_FLOAT, SHADER_UNIFORM_INT, SHADER_UNIFORM_VEC2, SHADER_UNIFORM_VEC3, BLEND_SUBTRACT_COLORS, BLANK

# --- Type Checking ---
if TYPE_CHECKING: from main import Game
if TYPE_CHECKING: from player import Player
if TYPE_CHECKING: from level import Level
