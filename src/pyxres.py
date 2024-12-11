import sys
import os

if getattr(sys, 'frozen', False):
    # PyInstallerで実行されている場合
    resource_path = os.path.join(sys._MEIPASS, 'art', 'common.pyxpal'), os.path.join(sys._MEIPASS, 'art', 'common.pyxres')
else:
    # 通常のPython実行時
    resource_path = os.path.join('..', 'art', 'common.pyxpal'), os.path.join('..', 'art', 'common.pyxres')

PYXPAL_PATH = resource_path[0]
PYXRES_PATH = resource_path[1]

TILE_SIZE_PX = 8

EMPTY_TILE_COOR = (0, 0)
BLOCK_TILE_COOR = (8, 0)

TILE_COLOR_PALLETS_NUMBER = 3
DEFAULT_COLOR_S = 1
RED_COLOR_S = 4
BLUE_COLOR_S = 7
GREEN_COLOR_S = 10
YELLOW_COLOR_S = 13

COLOR_SUCCESSFULL = 17
COLOR_FAILURE = 18

CHAR_WIDTH_PX = 4
CHAR_HEIGHT_PX = 5
