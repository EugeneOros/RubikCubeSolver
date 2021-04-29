import os
from enum import Enum

# Global
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Colors


# Camera interface
MINI_STICKER_AREA_TILE_SIZE = 14
MINI_STICKER_AREA_TILE_GAP = 2
MINI_STICKER_AREA_OFFSET = 20

STICKER_AREA_TILE_SIZE = 30
STICKER_AREA_TILE_GAP = 4
STICKER_AREA_OFFSET = 20

TEXT_SIZE = 10


class AppColors:
    PLACEHOLDER = (43, 43, 43)
    STICKER_CONTOUR = (230, 245, 93)


class Moves:
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"
    FRONT = "F"
    BACK = "B"
    LEFT_PRIM = "L'"
    RIGHT_PRIM = "R'"
    UP_PRIM = "U'"
    DOWN_PRIM = "D'"
    FRONT_PRIM = "F'"
    BACK_PRIM = "B'"


class AppMode(Enum):
    CALIBRATION = 1
    SCANNING = 2
    SOLVING = 3


class RotationCube:
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"


class Keys:
    SPACE = 32
    ESC = 27
    C_KEY = ord("c")
    S_KEY = ord("s")
    ENTER = 13


class ColorBlock:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Errors:
    INCORRECTLY_SCANNED = 1
    ALREADY_SOLVED = 2
    STOP = 3
    INCORRECTLY_SCRAMBLED = 4


class ConfigKeys:
    CUBE_PALETTE = 'cube_palette'
