from ..view import CenteredArea
from ..limitter import LimitableArea, Surface
from src.pyxres import CHAR_HEIGHT_PX, CHAR_WIDTH_PX

import pyxel

from typing import *

class WritenText(LimitableArea, CenteredArea):
    def __init__(self, cx, cy, text: str, color: int, scale: float = 3.0, parent_surface: Optional[Surface] = None):
        self.background_color = 1 if color == 0 else 0
        self.scale = scale
        self.img = self.__draw_text(text, color, self.background_color)

        super().__init__(0, 0, self.img.width * scale, self.img.height * scale)
        self.to_center_pos(cx, cy)
        self.set_limiteds(parent_surface)
    
    def rewrite(self, text: str, color: int):
        self.background_color = 1 if color == 0 else 0
        self.img = self.__draw_text(text, color, self.background_color)

        cx, cy = self.get_center_pos()
        self.w, self.h = self.img.width * self.scale, self.img.height * self.scale
        self.to_center_pos(cx, cy)
        
    @staticmethod
    def __draw_text(text: str, color: int, background_color: int):
        t_w = max(0, len(text) * CHAR_WIDTH_PX - 1)
        img = pyxel.Image(t_w, CHAR_HEIGHT_PX)
        img.cls(background_color)
        img.text(0, 0, text, color, None)
        return img

    def draw(self):
        cx, cy = self.get_center_pos()
        self.drawer.blt(
            cx - self.img.width // 2,
            cy - self.img.height // 2,
            self.img,
            0, 0,
            self.img.width,
            self.img.height,
            colkey=self.background_color,
            scale=self.scale
        )
