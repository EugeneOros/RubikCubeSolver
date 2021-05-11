import numpy as np
import cv2
from .helpers import ciede2000, bgr2lab
from config import config
from constants import AppColors, ConfigKeys


class ColorDetection:

    def __init__(self):
        self.prominent_color_palette = {
            'red': (0, 0, 255),
            'orange': (0, 165, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'white': (255, 255, 255),
            'yellow': (0,255,255)
        }

        self.cube_color_palette = config.get_setting(ConfigKeys.CUBE_PALETTE, self.prominent_color_palette)
        for side, bgr in self.cube_color_palette.items():
            self.cube_color_palette[side] = tuple(bgr)

    def get_prominent_color(self, bgr):
        """Get the prominent color equivalent of the given bgr color."""
        for color_name, color_bgr in self.cube_color_palette.items():
            if tuple([int(c) for c in bgr]) == color_bgr:
                return self.prominent_color_palette[color_name]
        return AppColors.PLACEHOLDER

    @staticmethod
    def get_dominant_color(roi):
        """
        Get dominant color from a certain region of interest.

        :param roi: The image list.
        :returns: tuple
        """
        pixels = np.float32(roi.reshape(-1, 3))
        n_colors = 1
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)
        dominant = palette[np.argmax(counts)]
        return tuple(dominant)

    def get_closest_color(self, bgr):
        """Get the closest color of a BGR color using CIEDE2000 distance."""
        lab = bgr2lab(bgr)
        distances = []
        for color_name, color_bgr in self.cube_color_palette.items():
            distances.append({
                'color_name': color_name,
                'color_bgr': color_bgr,
                'distance': ciede2000(lab, bgr2lab(color_bgr))
            })
        closest = min(distances, key=lambda item: item['distance'])
        return closest

    def convert_bgr_to_notation(self, bgr):
        notations = {
            'green': 'F',
            'white': 'U',
            'blue': 'B',
            'red': 'R',
            'orange': 'L',
            'yellow': 'D'
        }
        color_name = self.get_closest_color(bgr)['color_name']
        return notations[color_name]

    def set_cube_color_palette(self, palette):
        for side, bgr in palette.items():
            self.cube_color_palette[side] = tuple([int(c) for c in bgr])


color_detector = ColorDetection()
