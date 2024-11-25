from .view import View, Area
import pyxel

class Cursor(Area, View):
    def __init__(self):
        super().__init__(pyxel.mouse_x, pyxel.mouse_y, 0, 0)
    
    def update(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y

    def draw(self):
        pass
