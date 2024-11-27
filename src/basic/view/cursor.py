from .view import View, CenteredArea
from .limitter import LimitedDrawer
from .piece import PieceHolder
from ..rule.rule import Rotation

from typing import *

import pyxel

class Cursor(View, PieceHolder):
    def __init__(self):
        super().__init__(pyxel.mouse_x, pyxel.mouse_y, 0, 0)
        self.hold()
    
    def update(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y

    def draw(self, piece_rotation: Rotation, drawer: LimitedDrawer):
        self.held.draw(piece_rotation, drawer)
