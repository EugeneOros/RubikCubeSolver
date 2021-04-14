from src.constants import MINI_STICKER_AREA_TILE_GAP, MINI_STICKER_AREA_TILE_SIZE, MINI_STICKER_AREA_OFFSET, COLOR_PLACEHOLDER, STICKER_AREA_TILE_SIZE, \
    STICKER_AREA_TILE_GAP, STICKER_AREA_OFFSET
from src.video.color_detection import color_detector
import cv2

from src.video.helpers import render_text


class Scanner:
    def __init__(self, width, height):
        self.result_state = {}
        self.height = height
        self.width = width
        self.preview_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255)]
        self.snapshot_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                               (255, 255, 255), (255, 255, 255), (255, 255, 255),
                               (255, 255, 255), (255, 255, 255), (255, 255, 255)]

    def draw_stickers(self, frame, stickers, offset_x, offset_y):
        """Draws the given stickers onto the given frame."""
        index = -1
        for row in range(3):
            for col in range(3):
                index += 1
                x1 = (offset_x + STICKER_AREA_TILE_SIZE * col) + STICKER_AREA_TILE_GAP * col
                y1 = (offset_y + STICKER_AREA_TILE_SIZE * row) + STICKER_AREA_TILE_GAP * row
                x2 = x1 + STICKER_AREA_TILE_SIZE
                y2 = y1 + STICKER_AREA_TILE_SIZE

                # # shadow
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

    def draw_preview_stickers(self, frame):
        """Draw the current preview state onto the given frame."""
        self.draw_stickers(frame, self.preview_state, STICKER_AREA_OFFSET, STICKER_AREA_OFFSET)

    def draw_snapshot_stickers(self, frame):
        """Draw the current snapshot state onto the given frame."""
        y = STICKER_AREA_TILE_SIZE * 3 + STICKER_AREA_TILE_GAP * 2 + STICKER_AREA_OFFSET * 2
        self.draw_stickers(frame, self.snapshot_state, STICKER_AREA_OFFSET, y)

    def update_snapshot_state(self, frame):
        """Update the snapshot state based on the current preview state."""
        self.snapshot_state = list(self.preview_state)
        center_color_name = color_detector.get_closest_color(self.snapshot_state[4])['color_name']
        self.result_state[center_color_name] = self.snapshot_state
        self.draw_snapshot_stickers(frame)

    def draw_scanned_sides(self, frame):
        """Display how many sides are scanned by the user."""
        text = 'scanned sides: {}/6'.format(len(self.result_state.keys()))
        # print(text)
        render_text(frame, text, (20, self.height - 20), bottomLeftOrigin=True)

    def scanned_successfully(self):
        """Validate if the user scanned 9 colors for each side."""
        color_count = {}
        for side, preview in self.result_state.items():
            for bgr in preview:
                key = str(bgr)
                if key not in color_count:
                    color_count[key] = 1
                else:
                    color_count[key] = color_count[key] + 1
        invalid_colors = [k for k, v in color_count.items() if v != 9]
        return len(invalid_colors) == 0

    def draw_2d_cube_state(self, frame):
        """
        Create a 2D cube state visualization and draw the self.result_state.

        We're gonna display the visualization like so:
                    -----
                  | W W W |
                  | W W W |
                  | W W W |
            -----   -----   -----   -----
          | O O O | G G G | R R R | B B B |
          | O O O | G G G | R R R | B B B |
          | O O O | G G G | R R R | B B B |
            -----   -----   -----   -----
                  | Y Y Y |
                  | Y Y Y |
                  | Y Y Y |
                    -----
        So we're gonna make a 4x3 grid and hardcode where each side has to go.
        Based on the x and y in that 4x3 grid we can calculate its position.
        """
        grid = {
            'white': [1, 0],
            'orange': [0, 1],
            'green': [1, 1],
            'red': [2, 1],
            'blue': [3, 1],
            'yellow': [1, 2],
        }

        # The offset in-between each side (white, red, etc).
        side_offset = MINI_STICKER_AREA_TILE_GAP * 3

        # The size of 1 whole side (containing 9 stickers).
        side_size = MINI_STICKER_AREA_TILE_SIZE * 3 + MINI_STICKER_AREA_TILE_GAP * 2

        # The X and Y offset is placed in the bottom-right corner, minus the
        # whole size of the 4x3 grid, minus an additional offset.
        offset_x = self.width - (side_size * 4) - (side_offset * 3) - MINI_STICKER_AREA_OFFSET
        offset_y = self.height - (side_size * 3) - (side_offset * 2) - MINI_STICKER_AREA_OFFSET

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

                    foreground_color = COLOR_PLACEHOLDER
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
