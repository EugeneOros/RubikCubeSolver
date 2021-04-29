from constants import MINI_STICKER_AREA_TILE_GAP, MINI_STICKER_AREA_TILE_SIZE, MINI_STICKER_AREA_OFFSET, AppColors, STICKER_AREA_TILE_SIZE, \
    STICKER_AREA_TILE_GAP, STICKER_AREA_OFFSET
from video.color_detection import color_detector
import cv2

from video.helpers import render_text


class Scanner:
    def __init__(self, width, height):
        self.result_state = {}
        self.height = height
        self.width = width
        self.average_sticker_colors = {}
        self.preview_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255)]
        self.snapshot_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                               (255, 255, 255), (255, 255, 255), (255, 255, 255),
                               (255, 255, 255), (255, 255, 255), (255, 255, 255)]

    def scanned_all_sides(self):
        return len(self.result_state.keys()) == 6

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
        self.draw_stickers(frame, self.preview_state, STICKER_AREA_OFFSET+25, STICKER_AREA_OFFSET+100)

    def draw_snapshot(self, frame):
        y = STICKER_AREA_TILE_SIZE * 3 + STICKER_AREA_TILE_GAP * 2 + STICKER_AREA_OFFSET * 2
        # self.draw_stickers(frame, self.snapshot_state, STICKER_AREA_OFFSET, y)

    def draw_scrambled_mode(self, frame):
        render_text(frame, "Scramble mode ON", (400,470))

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

    def update_snapshot_state(self, frame):
        self.snapshot_state = list(self.preview_state)
        center_color_name = color_detector.get_closest_color(self.snapshot_state[4])['color_name']
        self.result_state[center_color_name] = self.snapshot_state
        self.draw_snapshot(frame)

    def draw_scanned_sides(self, frame):
        text = 'scanned sides: {}/6'.format(len(self.result_state.keys()))
        if len(self.result_state.keys()) == 6:
            render_text(frame, "press S to solve cube", (20, 80),)
        else:
            render_text(frame, "press C to calibrate", (20, 80), )
        render_text(frame, text, (20, 40))

    def draw_2d_cube_state(self, frame):
        grid = {
            'white': [1, 0],
            'orange': [0, 1],
            'green': [1, 1],
            'red': [2, 1],
            'blue': [3, 1],
            'yellow': [1, 2],
        }

        side_offset = MINI_STICKER_AREA_TILE_GAP * 3

        # The size of 1 whole side (containing 9 stickers).
        side_size = MINI_STICKER_AREA_TILE_SIZE * 3 + MINI_STICKER_AREA_TILE_GAP * 2

        # The X and Y offset is placed in the bottom-right corner, minus the
        # whole size of the 4x3 grid, minus an additional offset.
        offset_x = 20  # (side_size * 4) + (side_offset * 3) + MINI_STICKER_AREA_OFFSET
        offset_y = self.height - (side_size * 4) - (side_offset * 2) - MINI_STICKER_AREA_OFFSET

        for side, (grid_x, grid_y) in grid.items():
            index = -1
            for row in range(3):
                for col in range(3):
                    index += 1
                    x1 = int((offset_x + MINI_STICKER_AREA_TILE_SIZE * col) + (MINI_STICKER_AREA_TILE_GAP * col) + (
                            (side_size + side_offset) * grid_x))
                    y1 = int((offset_y + MINI_STICKER_AREA_TILE_SIZE * row) + (MINI_STICKER_AREA_TILE_GAP * row) + (
                            (side_size + side_offset) * grid_y))
                    x2 = int(x1 + MINI_STICKER_AREA_TILE_SIZE)
                    y2 = int(y1 + MINI_STICKER_AREA_TILE_SIZE)

                    foreground_color = AppColors.PLACEHOLDER
                    if side in self.result_state:
                        foreground_color = color_detector.get_prominent_color(self.result_state[side][index])

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
                        foreground_color,
                        -1
                    )
