from ..view import Area, View
from pyxres import CHAR_HEIGHT_PX, CHAR_WIDTH_PX

import pyxel

from typing import *

class ResultSheetView(Area, View):
    BORDER_THICKNESS_PX = 5

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.visibility = False
        self.title = self.__get_typo_image('RESULT', 0)
    
    def show(self):
        self.visibility = True
    
    def __get_typo_image(self, value: str, color: int):
        self.t_w = max(0, len(value) * CHAR_WIDTH_PX - 1)
        img = pyxel.Image(self.t_w, CHAR_HEIGHT_PX)
        img.cls(1)
        img.text(0, 0, value, color, None)
        return img
    
    def update(self):
        pass

    def draw(self):
        if self.visibility:
            border = ResultSheetView.BORDER_THICKNESS_PX
            pyxel.rect(self.x, self.y, self.w, self.h, 16)
            pyxel.rect(self.x + border, self.y + border, self.w - border * 2, self.h - border * 2, 1)
            pyxel.blt(
                self.x + (self.w - self.t_w) / 2,
                self.y + 30,
                self.title,
                0, 0,
                self.t_w,
                CHAR_HEIGHT_PX,
                colkey=1,
                scale=3
            )
