from constants import MINI_STICKER_AREA_TILE_GAP, MINI_STICKER_AREA_TILE_SIZE, MINI_STICKER_AREA_OFFSET, AppColors, STICKER_AREA_TILE_SIZE, \
    STICKER_AREA_TILE_GAP, STICKER_AREA_OFFSET
from video.color_detection import color_detector
import cv2
from .helpers import render_text, get_text_size


from constants import (
    AppColors,
    Keys,
    Errors,
    Moves,
    RotationCube,
    AppMode
)


class Solver:
    def __init__(self, width, height):
        self.height = height
        self.width = width

    def draw_error(self, frame, error):
        if error == Errors.INCORRECTLY_SCANNED:
            y_offset = 30
            text = 'Oops, you did not scan in all 6 sides correctly'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Oops, you did not scan in all 6 sides correctly', (int(self.width / 2 - text_size_width / 2), y_offset))
            text = 'Press S to try again.'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Press S to try again.', (int(self.width / 2 - text_size_width / 2), y_offset+30))
        elif error == Errors.ALREADY_SOLVED:
            y_offset = 30
            text = 'Cube has already been solved'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Cube has already been solved', (int(self.width / 2 - text_size_width / 2), y_offset))
            text = 'Press ESC to finish'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Press ESC to finish', (int(self.width / 2 - text_size_width / 2), y_offset + 30))
