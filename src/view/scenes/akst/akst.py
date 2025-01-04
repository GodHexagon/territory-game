from ...view import View, Area
from src.pyxres import *
from ...areas.text import WritenText
from ...areas.button import Button

import pyxel

from typing import *

class AccessKeySettingScene(View, Area):
    def __init__(self, x: float, y: float, w: float, h: float, on_complete: Callable[[bool], None]) -> None:
        super().__init__(x, y, w, h)
        self.window = Window(*self.get_center_pos(), on_complete)
    
    def update(self):
        pass

    def draw(self):
        pyxel.cls(COLOR_WHITE)
        self.window.draw()

class Window(Area):
    SIZE_PX = (500, 200)
    MARGIN_PX = 16

    def __init__(self, cx: float, cy: float, on_complete: Callable[[bool], None]) -> None:
        super().__init__(0, 0, *Window.SIZE_PX)
        self.to_center_pos(cx, cy)

        MARGIN = Window.MARGIN_PX

        self.title = WritenText(cx, 0, text="SET YOUR ACCESS KEY", color=COLOR_BLACK, scale=5)
        self.title.to_y(self.y + MARGIN)

        self.update_b = Button(0, 0, "UPDATE", lambda : on_complete(True))
        self.update_b.to_x_end(self.x + self.w - MARGIN)
        self.update_b.to_y_bottom(self.y + self.h - MARGIN)
    
    def update(self):
        self.update_b.update()
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.title.draw()
        self.update_b.draw()
