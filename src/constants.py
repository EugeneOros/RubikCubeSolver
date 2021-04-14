import os

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


class Keys:
    SPACE = 32
    ESC = 27
    C_KEY = ord("c")


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


class ConfigKeys:
    CUBE_PALETTE = 'cube_palette'
