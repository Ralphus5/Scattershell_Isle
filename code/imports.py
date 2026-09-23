"""Explicit imports are done for functions that are actually used. Expections are os, sys, json and re, 
where objects are prefixed. For datetime, one should mind, that it contains datetime.datetime!
In addition, every module is imported for auto-completion look-ups."""

import pyray
from pyray import (Image, Texture, Vector2, Color, WHITE, BLACK, RED, GRAY, RAYWHITE, PURPLE, DARKPURPLE, DARKGRAY, LIGHTGRAY,
                   Rectangle, Font, draw_texture_ex, draw_line, draw_text_ex, draw_rectangle_lines, draw_rectangle_rec, 
                   begin_texture_mode, end_texture_mode, begin_drawing, end_drawing, begin_mode_2d, end_mode_2d, load_texture, 
                   set_music_volume, measure_text_ex, draw_texture_pro, vector2_add, vector2_subtract, vector2_length, 
                   vector2_normalize, Camera2D, clamp, check_collision_recs, check_collision_circle_rec, vector2_negate, 
                   clear_background, draw_texture, set_exit_key, window_should_close, get_frame_time, update_music_stream,
                   toggle_fullscreen, hide_cursor, is_window_fullscreen, show_cursor, is_key_down, is_key_pressed, get_time,
                   draw_rectangle_lines_ex, draw_rectangle, get_screen_height, get_screen_width, init_window, init_audio_device,
                   set_target_fps, load_render_texture, load_image, set_window_icon, load_font_ex, ffi, Music, Sound, load_sound,
                   load_music_stream, is_gamepad_available, get_gamepad_axis_movement, is_gamepad_button_down, is_gamepad_button_pressed,
                   stop_music_stream, play_music_stream, pause_music_stream, resume_music_stream, get_random_value, set_sound_pitch,
                   play_sound, set_sound_volume, close_audio_device, close_window, draw_triangle, draw_line_ex, vector2_add_value)
import pytmx
from pytmx import TiledMap
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
from raylib import  KEY_A, KEY_D, KEY_S, KEY_W, KEY_Q, KEY_E, KEY_R, KEY_T, KEY_Z, KEY_U, KEY_I, \
KEY_O, KEY_P, KEY_F, KEY_G, KEY_H, KEY_J, KEY_K, KEY_L, KEY_Y, KEY_X, KEY_C, KEY_V, KEY_B, KEY_N, \
KEY_M, KEY_LEFT_SHIFT, KEY_RIGHT_SHIFT, KEY_BACK, KEY_ENTER, KEY_SPACE, KEY_ESCAPE, KEY_TAB, \
KEY_F11, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_BACKSPACE, KEY_RIGHT_SUPER, KEY_LEFT_SUPER

from raylib import GAMEPAD_AXIS_LEFT_X, GAMEPAD_AXIS_LEFT_Y, GAMEPAD_AXIS_RIGHT_X, GAMEPAD_AXIS_RIGHT_Y, \
GAMEPAD_BUTTON_LEFT_FACE_DOWN, GAMEPAD_BUTTON_LEFT_FACE_LEFT, GAMEPAD_BUTTON_LEFT_FACE_RIGHT, GAMEPAD_BUTTON_LEFT_FACE_UP, \
GAMEPAD_BUTTON_MIDDLE_RIGHT, GAMEPAD_BUTTON_MIDDLE_LEFT, GAMEPAD_BUTTON_MIDDLE, GAMEPAD_BUTTON_LEFT_TRIGGER_1, \
GAMEPAD_BUTTON_LEFT_TRIGGER_2, GAMEPAD_BUTTON_RIGHT_TRIGGER_1, GAMEPAD_BUTTON_RIGHT_TRIGGER_2, GAMEPAD_BUTTON_RIGHT_FACE_DOWN, \
GAMEPAD_BUTTON_RIGHT_FACE_UP, GAMEPAD_BUTTON_RIGHT_FACE_LEFT, GAMEPAD_BUTTON_RIGHT_FACE_RIGHT

# --- Type Checking ---
if TYPE_CHECKING: from main import Game
if TYPE_CHECKING: from player import player
if TYPE_CHECKING: from enemy import enemy
