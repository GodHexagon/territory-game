from .view import View, Area
from typing import *

from abc import ABC
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
    
    def hold(self, by: Optional['Followable'] = None):
        if by is not None: by.follow(self)
        self.held = by
    
    def is_holding(self):
        return self.held is not None

class Followable(ABC):
    def follow(self, to: Cursor):
        self.following_to = to
    
    def set_visibility(self, visible: bool):
        self.visibility = visible
