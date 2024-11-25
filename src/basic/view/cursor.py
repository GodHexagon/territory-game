from .view import View, Area
from typing import *
import pyxel

class Cursor(Area, View):
    def __init__(self):
        super().__init__(pyxel.mouse_x, pyxel.mouse_y, 0, 0)
        self.held: Followable | None = None
    
    def update(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y

    def draw(self):
        pass
    
    def hold(self, thing):
        self.held = thing
    
    def is_holding(self):
        return self.held is not None

class Followable:
    def follow(self, to: Cursor, relative_pos: Tuple[int, int]):
        self.relative_pos = relative_pos
        self.following_to = to
