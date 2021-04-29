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
        self.average_sticker_colors = {}
        self.preview_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255)]
        self.snapshot_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                               (255, 255, 255), (255, 255, 255), (255, 255, 255),
                               (255, 255, 255), (255, 255, 255), (255, 255, 255)]

    def draw_error(self, frame, error):
        if error == Errors.INCORRECTLY_SCANNED:
            y_offset = 30
            text = 'Oops, you did not scan in all 6 sides correctly'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Oops, you did not scan in all 6 sides correctly', (int(self.width / 2 - text_size_width / 2), y_offset))
            text = 'Press ENTER to try again.'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Press S to try again.', (int(self.width / 2 - text_size_width / 2), y_offset + 30))
        elif error == Errors.ALREADY_SOLVED:
            y_offset = 30
            text = 'Cube has already been solved'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Cube has already been solved', (int(self.width / 2 - text_size_width / 2), y_offset))
            text = 'Press ESC to finish'
            (text_size_width, text_size_height), _ = get_text_size(text)
            render_text(frame, 'Press ESC to finish', (int(self.width / 2 - text_size_width / 2), y_offset + 30))

    @staticmethod
    def draw_stickers(frame, stickers, offset_x, offset_y):
        index = -1
        for row in range(3):
            for col in range(3):
                index += 1
                x1 = (offset_x + STICKER_AREA_TILE_SIZE * col) + STICKER_AREA_TILE_GAP * col
                y1 = (offset_y + STICKER_AREA_TILE_SIZE * row) + STICKER_AREA_TILE_GAP * row
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

                # foreground color
                cv2.rectangle(
                    frame,
                    (x1 + 1, y1 + 1),
                    (x2 - 1, y2 - 1),
                    color_detector.get_prominent_color(stickers[index]),
                    -1
                )

    def draw_preview(self, frame):
        self.draw_stickers(frame, self.preview_state, STICKER_AREA_OFFSET + 25, STICKER_AREA_OFFSET + 100)

    # def draw_snapshot(self, frame):
    #     y = STICKER_AREA_TILE_SIZE * 3 + STICKER_AREA_TILE_GAP * 2 + STICKER_AREA_OFFSET * 2
    #     # self.draw_stickers(frame, self.snapshot_state, STICKER_AREA_OFFSET, y)

    # def draw_scrambled_mode(self, frame):
    #     render_text(frame, "Scramble mode ON", (400, 470))

    def update_preview_state(self, frame, contours):
        max_average_rounds = 8
        for index, (x, y, w, h) in enumerate(contours):
            if index in self.average_sticker_colors and len(self.average_sticker_colors[index]) == max_average_rounds:
                sorted_items = {}
                for bgr in self.average_sticker_colors[index]:
                    key = str(bgr)
                    if key in sorted_items:
                        sorted_items[key] += 1
                    else:
                        sorted_items[key] = 1
                most_common_color = max(sorted_items, key=lambda i: sorted_items[i])
                self.average_sticker_colors[index] = []
                self.preview_state[index] = eval(most_common_color)
                break

            roi = frame[y + 7:y + h - 7, x + 14:x + w - 14]
            avg_bgr = color_detector.get_dominant_color(roi)
            closest_color = color_detector.get_closest_color(avg_bgr)['color_bgr']
            self.preview_state[index] = closest_color
            if index in self.average_sticker_colors:
                self.average_sticker_colors[index].append(closest_color)
            else:
                self.average_sticker_colors[index] = [closest_color]
