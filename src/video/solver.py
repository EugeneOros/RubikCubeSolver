from constants import MINI_STICKER_AREA_TILE_GAP, MINI_STICKER_AREA_TILE_SIZE, MINI_STICKER_AREA_OFFSET, AppColors, STICKER_AREA_TILE_SIZE, \
    STICKER_AREA_TILE_GAP, STICKER_AREA_OFFSET
from rubik.maths import Point
from video.color_detection import color_detector
import cv2
from .helpers import render_text, get_text_size
from rubik.cube import Cube

from constants import (
    AppColors,
    Keys,
    Errors,
    Moves,
    RotationCube,
    AppMode,
    CubePosition,
)


class Solver:
    moves = []
    current_move_index = None
    back_move_count = 3

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.cube = None
        self.average_sticker_colors = {}
        self.preview_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255),
                              (255, 255, 255), (255, 255, 255), (255, 255, 255)]
        self.expected_side_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                                    (255, 255, 255), (255, 255, 255), (255, 255, 255),
                                    (255, 255, 255), (255, 255, 255), (255, 255, 255)]
        self.expected_result_state = [(255, 255, 255), (255, 255, 255), (255, 255, 255),
                                      (255, 255, 255), (255, 255, 255), (255, 255, 255),
                                      (255, 255, 255), (255, 255, 255), (255, 255, 255)]

    def set_cube(self, cube_str, algorithm_str):
        self.cube = Cube(cube_str)
        print(algorithm_str)

        for move in algorithm_str.split(" "):
            if move == move[0] + "2":
                self.append_move_from_str(move[0])
                self.append_move_from_str(move[0])
                # self.moves.append(self.get_move_from_str(move[0]))
                # self.moves.append(self.get_move_from_str(move[0]))
            else:
                self.append_move_from_str(move)
        print(self.moves)
        self.next_move()
        # self.current_move_index = 0
        # state = []
        # for i in self.return_side(self.cube, CubePosition.FRONT):
        #     color = color_detector.convert_letter_to_color(i)
        #     state.append(color)
        # self.expected_side_state = state
        # self.cube.Li()
        # state = []
        # for i in self.return_side(self.cube, CubePosition.FRONT):
        #     color = color_detector.convert_letter_to_color(i)
        #     state.append(color)
        # self.expected_result_state = state

    def append_move_from_str(self, string):
        if string == "R":
            self.moves.append(Moves.RIGHT)
        elif string == "L":
            self.moves.append(Moves.LEFT)
        elif string == "F":
            self.moves.append(Moves.FRONT)
        elif string == "U":
            self.moves.append(Moves.UP)
        elif string == "D":
            self.moves.append(Moves.DOWN)
        elif string == "R'":
            self.moves.append(Moves.RIGHT_PRIM)
        elif string == "L'":
            self.moves.append(Moves.LEFT_PRIM)
        elif string == "F'":
            self.moves.append(Moves.FRONT_PRIM)
        elif string == "U'":
            self.moves.append(Moves.UP_PRIM)
        elif string == "D'":
            self.moves.append(Moves.DOWN_PRIM)
        elif string == "B":
            self.moves.append(Moves.BACK)
            # self.moves.append(Moves.RIGHT_ROTATE)
            # self.moves.append(Moves.RIGHT)
            # self.moves.append(Moves.LEFT_ROTATE)
        elif string == "B'":
            self.moves.append(Moves.BACK_PRIM)
            # self.moves.append(Moves.RIGHT_ROTATE)
            # self.moves.append(Moves.LEFT)
            # self.moves.append(Moves.LEFT_ROTATE)

    def draw_moves_and_next(self, frame, contours):
        if self.preview_state == self.expected_side_state:
            if self.back_move_count == 0:
                self.draw_rotation(frame, contours, RotationCube.RIGHT)
            elif self.back_move_count == 1:
                if self.moves[self.current_move_index] == Moves.BACK:
                    self.draw_move(frame=frame, move=Moves.RIGHT, contours=contours)
                else:
                    self.draw_move(frame=frame, move=Moves.LEFT, contours=contours)
            elif self.back_move_count == 2:
                self.draw_rotation(frame, contours, RotationCube.LEFT)
            else:
                self.draw_move(frame=frame, move=self.moves[self.current_move_index], contours=contours)
        if self.preview_state == self.expected_result_state:
            print("next_done")
            self.next_move()

    def next_move(self):
        if self.current_move_index is None:
            self.current_move_index = 0
        else:
            if self.back_move_count == 3:
                self.current_move_index += 1
        state = []
        #
        # if self.back_move_count < 3:
        #     self.back_move_count += 1

        if self.moves[self.current_move_index] == Moves.BACK or self.moves[self.current_move_index] == Moves.BACK_PRIM:
            if self.back_move_count < 3:
                print(self.back_move_count)
                self.back_move_count += 1
            else:
                self.back_move_count = 0

        if self.back_move_count == 0:
            print("got 0")
            expected_side = CubePosition.FRONT
            result_side = CubePosition.RIGHT
        elif self.back_move_count == 1:
            print("got 1")
            result_side = expected_side = CubePosition.RIGHT
        elif self.back_move_count == 2:
            print("got 2")
            expected_side = CubePosition.RIGHT
            result_side = CubePosition.FRONT
        else:
            result_side = expected_side = CubePosition.FRONT

        for i in self.return_side(self.cube, expected_side):
            color = color_detector.convert_letter_to_color(i)
            state.append(color)
        self.expected_side_state = state

        if self.back_move_count == 1 or self.back_move_count == 3:
            self.make_cube_move(self.moves[self.current_move_index])

        state = []
        for i in self.return_side(self.cube, result_side):
            color = color_detector.convert_letter_to_color(i)
            state.append(color)
        self.expected_result_state = state

    def make_cube_move(self, move):
        if move == Moves.RIGHT:
            self.cube.R()
        elif move == Moves.LEFT:
            self.cube.L()
        elif move == Moves.FRONT:
            self.cube.F()
        elif move == Moves.UP:
            self.cube.U()
        elif move == Moves.DOWN:
            self.cube.D()
        elif move == Moves.RIGHT_PRIM:
            self.cube.Ri()
        elif move == Moves.LEFT_PRIM:
            self.cube.Li()
        elif move == Moves.FRONT_PRIM:
            self.cube.Fi()
        elif move == Moves.UP_PRIM:
            self.cube.Ui()
        elif move == Moves.DOWN_PRIM:
            self.cube.Di()
        elif move == Moves.BACK:
            self.cube.B()
        elif move == Moves.BACK_PRIM:
            self.cube.Bi()

    def draw_move(self, frame, contours, move):
        if len(contours) < 9:
            return
        start_index = None
        end_index = None
        if move == Moves.LEFT:
            start_index = 0
            end_index = 6
        elif move == Moves.RIGHT:
            start_index = 8
            end_index = 2
        elif move == Moves.UP:
            start_index = 2
            end_index = 0
        elif move == Moves.DOWN:
            start_index = 6
            end_index = 8
        elif move == Moves.LEFT_PRIM:
            start_index = 6
            end_index = 0
        elif move == Moves.RIGHT_PRIM:
            start_index = 2
            end_index = 8
        elif move == Moves.UP_PRIM:
            start_index = 0
            end_index = 2
        elif move == Moves.DOWN_PRIM:
            start_index = 8
            end_index = 6
        elif move == Moves.BACK or move == Moves.BACK_PRIM:
            start_index = 0
            end_index = 0

        if start_index is None or end_index is None:
            edge_indexes = [0, 2, 8, 6]
            if move == Moves.FRONT_PRIM:
                edge_indexes.reverse()
            for i in range(0, len(edge_indexes)):
                if i + 1 < len(edge_indexes):
                    end_index = edge_indexes[i + 1]
                else:
                    end_index = edge_indexes[0]
                self.draw_arrow(frame, contours[edge_indexes[i]], contours[end_index])

        else:
            self.draw_arrow(frame, contours[start_index], contours[end_index])

    def draw_rotation(self, frame, contours, rotation):
        if len(contours) < 9:
            return
        if rotation == RotationCube.LEFT:
            for i in range(0, 9, 3):
                self.draw_arrow(frame, contours[i], contours[i + 2])
        elif rotation == RotationCube.RIGHT:
            for i in range(8, -1, -3):
                self.draw_arrow(frame, contours[i], contours[i - 2])
        elif rotation == RotationCube.UP:
            for i in range(0, 3):
                self.draw_arrow(frame, contours[i], contours[i + 6])
        elif rotation == RotationCube.DOWN:
            for i in range(6, 9):
                self.draw_arrow(frame, contours[i], contours[i - 6])

    def draw_arrow(self, frame, contour_start, contour_end):
        (x_start, y_start, w_start, h_start) = contour_start
        x_start = x_start + int(w_start / 2)
        y_start = y_start + int(h_start / 2)
        (x_end, y_end, w_end, h_end) = contour_end
        x_end = x_end + int(w_end / 2)
        y_end = y_end + int(h_end / 2)
        point_start = (x_start, y_start)
        point_end = (x_end, y_end)
        cv2.arrowedLine(frame, point_start, point_end, AppColors.PLACEHOLDER, 7, tipLength=0.2)
        cv2.arrowedLine(frame, point_start, point_end, AppColors.STICKER_CONTOUR, 4, tipLength=0.2)

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
    def draw_stickers(frame, stickers, offset_x, offset_y, text):
        render_text(frame, text, (offset_x, offset_y))
        offset_y += 10
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
        self.draw_stickers(frame, self.preview_state, STICKER_AREA_OFFSET + 10, STICKER_AREA_OFFSET + 20, "preview")

    def draw_expected_side(self, frame):
        self.draw_stickers(frame, self.expected_side_state, STICKER_AREA_OFFSET + 10, STICKER_AREA_OFFSET + 170, "expected side")

    def draw_expected_result(self, frame):
        self.draw_stickers(frame, self.expected_result_state, STICKER_AREA_OFFSET + 10, STICKER_AREA_OFFSET + 320, "expected result")

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

    def _color_list(self, cube, cube_position):
        if cube_position == CubePosition.RIGHT:
            return [p.colors[0] for p in sorted(self._face(CubePosition.RIGHT, cube), key=lambda p: (-p.pos.y, -p.pos.z))]
        elif cube_position == CubePosition.LEFT:
            return [p.colors[0] for p in sorted(self._face(CubePosition.LEFT, cube), key=lambda p: (-p.pos.y, p.pos.z))]
        elif cube_position == CubePosition.UP:
            return [p.colors[1] for p in sorted(self._face(CubePosition.UP, cube), key=lambda p: (p.pos.z, p.pos.x))]

        elif cube_position == CubePosition.DOWN:
            return [p.colors[1] for p in sorted(self._face(CubePosition.DOWN, cube), key=lambda p: (-p.pos.z, p.pos.x))]

        elif cube_position == CubePosition.FRONT:
            return [p.colors[2] for p in sorted(self._face(CubePosition.FRONT, cube), key=lambda p: (-p.pos.y, p.pos.x))]

        elif cube_position == CubePosition.BACK:
            return [p.colors[2] for p in sorted(self._face(CubePosition.BACK, cube), key=lambda p: (-p.pos.y, -p.pos.x))]

    def _face(self, axis, cube):
        assert axis.count(0) == 2
        return [p for p in cube.pieces if p.pos.dot(axis) > 0]

    def return_side(self, cube, cube_position):
        color_list = self._color_list(cube, cube_position)
        return color_list
