import cv2
from .color_detection import color_detector
from .helpers import Keys
from .calibration import Calibration
from .scanner import Scanner
from src.constants import (
    STICKER_CONTOUR_COLOR,
    CALIBRATE_MODE_KEY,
    E_INCORRECTLY_SCANNED,
    E_ALREADY_SOLVED
)


class Webcam:

    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.average_sticker_colors = {}

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.calibration = Calibration(self.width)
        self.scanner = Scanner(self.width, self.height)

    @staticmethod
    def find_contours(dilated_frame):
        """Find the contours of a 3x3x3 cube."""
        contours, hierarchy = cv2.findContours(dilated_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        final_contours = []

        # Step 1/4: filter all contours to only those that are square-ish shapes.
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.1 * perimeter, True)
            if len(approx) == 4:
                area = cv2.contourArea(contour)
                (x, y, w, h) = cv2.boundingRect(approx)

                # Find aspect ratio of boundary rectangle around the countours.
                ratio = w / float(h)

                # Check if contour is close to a square.
                if 0.8 <= ratio <= 1.2 and 30 <= w <= 60 and area / (w * h) > 0.4:
                    final_contours.append((x, y, w, h))

        # Return early if we didn't found 9 or more contours.
        if len(final_contours) < 9:
            return []

        # Step 2/4: Find the contour that has 9 neighbors (including itself)
        # and return all of those neighbors.
        found = False
        contour_neighbors = {}
        for index, contour in enumerate(final_contours):
            (x, y, w, h) = contour
            contour_neighbors[index] = []
            center_x = x + w / 2
            center_y = y + h / 2
            radius = 1.5

            # Create 9 positions for the current contour which are the
            # neighbors. We'll use this to check how many neighbors each contour
            # has. The only way all of these can match is if the current contour
            # is the center of the cube. If we found the center, we also know
            # all the neighbors, thus knowing all the contours and thus knowing
            # this shape can be considered a 3x3x3 cube. When we've found those
            # contours, we sort them and return them.
            neighbor_positions = [
                # top left
                [(center_x - w * radius), (center_y - h * radius)],

                # top middle
                [center_x, (center_y - h * radius)],

                # top right
                [(center_x + w * radius), (center_y - h * radius)],

                # middle left
                [(center_x - w * radius), center_y],

                # center
                [center_x, center_y],

                # middle right
                [(center_x + w * radius), center_y],

                # bottom left
                [(center_x - w * radius), (center_y + h * radius)],

                # bottom middle
                [center_x, (center_y + h * radius)],

                # bottom right
                [(center_x + w * radius), (center_y + h * radius)],
            ]

            for neighbor in final_contours:
                (x2, y2, w2, h2) = neighbor
                for (x3, y3) in neighbor_positions:
                    # The neighbor_positions are located in the center of each
                    # contour instead of top-left corner.
                    # logic: (top left < center pos) and (bottom right > center pos)
                    if (x2 < x3 and y2 < y3) and (x2 + w2 > x3 and y2 + h2 > y3):
                        contour_neighbors[index].append(neighbor)

        # Step 3/4: Now that we know how many neighbors all contours have, we'll
        # loop over them and find the contour that has 9 neighbors, which
        # includes itself. This is the center piece of the cube. If we come
        # across it, then the 'neighbors' are actually all the contours we're
        # looking for.
        for (contour, neighbors) in contour_neighbors.items():
            if len(neighbors) == 9:
                found = True
                final_contours = neighbors
                break

        if not found:
            return []

        # Step 4/4: When we reached this part of the code we found a cube-like
        # contour. The code below will sort all the contours on their X and Y
        # values from the top-left to the bottom-right.

        # Sort contours on the y-value first.
        y_sorted = sorted(final_contours, key=lambda item: item[1])

        # Split into 3 rows and sort each row on the x-value.
        top_row = sorted(y_sorted[0:3], key=lambda item: item[0])
        middle_row = sorted(y_sorted[3:6], key=lambda item: item[0])
        bottom_row = sorted(y_sorted[6:9], key=lambda item: item[0])

        sorted_contours = top_row + middle_row + bottom_row
        return sorted_contours

    def draw_contours(self, frame, contours):
        """Draw contours onto the given frame."""
        if self.calibration.calibrate_mode:
            # Only show the center piece contour.
            (x, y, w, h) = contours[4]
            cv2.rectangle(frame, (x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)
        else:
            for index, (x, y, w, h) in enumerate(contours):
                cv2.rectangle(frame, (x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)

    def update_preview_state(self, frame, contours):
        """
        Get the average color value for the contour for every X amount of frames
        to prevent flickering and more precise results.
        """
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
                self.scanner.preview_state[index] = eval(most_common_color)
                break

            roi = frame[y + 7:y + h - 7, x + 14:x + w - 14]
            avg_bgr = color_detector.get_dominant_color(roi)
            closest_color = color_detector.get_closest_color(avg_bgr)['color_bgr']
            self.scanner.preview_state[index] = closest_color
            if index in self.average_sticker_colors:
                self.average_sticker_colors[index].append(closest_color)
            else:
                self.average_sticker_colors[index] = [closest_color]

    def update_snapshot_state(self, frame):
        """Update the snapshot state based on the current preview state."""
        self.scanner.snapshot_state = list(self.scanner.preview_state)
        center_color_name = color_detector.get_closest_color(self.scanner.snapshot_state[4])['color_name']
        self.scanner.result_state[center_color_name] = self.scanner.snapshot_state
        self.scanner.draw_snapshot_stickers(frame)

    def get_result_notation(self):
        """Convert all the sides and their BGR colors to cube notation."""
        notation = dict(self.scanner.result_state)
        for side, preview in notation.items():
            for sticker_index, bgr in enumerate(preview):
                notation[side][sticker_index] = color_detector.convert_bgr_to_notation(bgr)

        # Join all the sides together into one single string.
        # Order must be URFDLB (white, red, green, yellow, orange, blue)
        combined = ''
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            combined += ''.join(notation[side])
        return combined

    def state_already_solved(self):
        """Find out if the cube hasn't been solved already."""
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            # Get the center color of the current side.
            center_bgr = self.scanner.result_state[side][4]

            # Compare the center color to all neighbors. If we come across a
            # different color, then we can assume the cube isn't solved yet.
            for bgr in self.scanner.result_state[side]:
                if center_bgr != bgr:
                    return False
        return True

    def run(self):
        """
        Open up the webcam and present the user with the Qbr user interface.

        Returns a string of the scanned state in rubik's cube notation.
        """
        while True:
            _, frame = self.cam.read()
            key = cv2.waitKey(10) & 0xff

            if key == Keys.ESC:
                break

            if not self.calibration.calibrate_mode:
                if key == Keys.SPACE:
                    self.update_snapshot_state(frame)

            # Toggle calibrate mode.
            if key == ord(CALIBRATE_MODE_KEY):
                self.calibration.reset_calibrate_mode()
                self.calibration.calibrate_mode = not self.calibration.calibrate_mode

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.blur(gray_frame, (3, 3))
            canny_frame = cv2.Canny(blurred_frame, 30, 60, 3)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            dilated_frame = cv2.dilate(canny_frame, kernel)

            contours = self.find_contours(dilated_frame)
            if len(contours) == 9:
                self.draw_contours(frame, contours)
                if not self.calibration.calibrate_mode:
                    self.update_preview_state(frame, contours)
                elif key == 32 and self.calibration.done_calibrating is False:
                    self.calibration.on_space_pressed(frame, contours)

            if self.calibration.calibrate_mode:
                self.calibration.draw_current_color_to_calibrate(frame)
                self.calibration.draw_calibrated_colors(frame)
            else:
                self.scanner.draw_preview_stickers(frame)
                self.scanner.draw_snapshot_stickers(frame)
                self.scanner.draw_scanned_sides(frame)
                self.scanner.draw_2d_cube_state(frame)

            cv2.imshow("Qbr - Rubik's cube solver", frame)

        self.cam.release()
        cv2.destroyAllWindows()

        if len(self.scanner.result_state.keys()) != 6:
            return E_INCORRECTLY_SCANNED

        if not self.scanner.scanned_successfully():
            return E_INCORRECTLY_SCANNED

        if self.state_already_solved():
            return E_ALREADY_SOLVED

        return self.get_result_notation()


webcam = Webcam()
