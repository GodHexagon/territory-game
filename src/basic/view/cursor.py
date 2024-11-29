from .view import View, Area
from .limitter import LimitableArea
from .piece import PieceHolder
from ..rule.rule import Rotation

from typing import *

import pyxel

class Cursor(View, PieceHolder):
    def __init__(self):
        super().__init__(pyxel.mouse_x, pyxel.mouse_y, 0, 0)
        self.hold()
        self.drawer = CursorField(0, 0, pyxel.width, pyxel.height).drawer
    
    def set_rotation(self, value: Rotation):
        self.rotation = value
    
    def update(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y

    def draw(self):
        if self.held is not None: self.held.draw(self.rotation, self.drawer)

class CursorField(LimitableArea):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.set_limiteds()
