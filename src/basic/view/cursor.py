from .view import View
import pyxel

class Cursor(View):
    def __init__(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y
    
    def update(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y
