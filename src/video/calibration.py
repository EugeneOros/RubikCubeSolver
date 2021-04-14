from src.constants import TEXT_SIZE, STICKER_AREA_TILE_SIZE, CUBE_PALETTE
from .helpers import render_text, get_text_size
from .color_detection import color_detector
from src.config import config
import cv2


class Calibration:
    def __init__(self, width):
        self.width = width
        self.calibrate_mode = False
        self.calibrated_colors = {}
        self.current_color_to_calibrate_index = 0
        self.done_calibrating = False
        self.colors_to_calibrate = ['green', 'red', 'blue', 'orange', 'white', 'yellow']

    def draw_current_color_to_calibrate(self, frame):
        """Display the current side's color that needs to be calibrated."""
        y_offset = 20
        font_size = int(TEXT_SIZE * 1.25)
        if self.done_calibrating:
            messages = [
                'Calibrated successfully',
                'Press c to quit calibrate mode',
            ]
            for index, text in enumerate(messages):
                print(text)
                # font_size
                (text_size_width, text_size_height), _ = get_text_size(text)
                y = y_offset + (text_size_height + 10) * index
                render_text(frame, text, (int(self.width / 2 - text_size_width / 2), y), size=font_size)
        else:
            current_color = self.colors_to_calibrate[self.current_color_to_calibrate_index]
            text = 'Calibrate the {} side'.format(current_color)
            (text_size_width, text_size_height), _ = get_text_size(text, font_size)
            render_text(frame, text, (int(self.width / 2 - text_size_width / 2), y_offset), size=font_size)

    def draw_calibrated_colors(self, frame):
        """Display all the colors that are calibrated while in calibrate mode."""
        offset_y = 20
        for index, (color_name, color_bgr) in enumerate(self.calibrated_colors.items()):
            x1 = 90
            y1 = int(offset_y + STICKER_AREA_TILE_SIZE * index)
            x2 = x1 + STICKER_AREA_TILE_SIZE
            y2 = y1 + STICKER_AREA_TILE_SIZE

            # shadow
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 0, 0),
                -1
            )

            # foreground
            cv2.rectangle(
                frame,
                (x1 + 1, y1 + 1),
                (x2 - 1, y2 - 1),
                tuple([int(c) for c in color_bgr]),
                -1
            )
            render_text(frame, color_name, (20, y1 + 3))

    def on_space_pressed(self, frame, contours):
        current_color = self.colors_to_calibrate[self.current_color_to_calibrate_index]
        (x, y, w, h) = contours[4]
        roi = frame[y + 7:y + h - 7, x + 14:x + w - 14]
        avg_bgr = color_detector.get_dominant_color(roi)
        self.calibrated_colors[current_color] = avg_bgr
        self.current_color_to_calibrate_index += 1
        self.done_calibrating = self.current_color_to_calibrate_index == len(self.colors_to_calibrate)
        if self.done_calibrating:
            color_detector.set_cube_color_palette(self.calibrated_colors)
            config.set_setting(CUBE_PALETTE, color_detector.cube_color_palette)

    def reset_calibrate_mode(self):
        """Reset calibrate mode variables."""
        self.calibrated_colors = {}
        self.current_color_to_calibrate_index = 0
        self.done_calibrating = False

