from ..view import CenteredArea
from ..limitter import LimitableArea, Surface
from src.pyxres import CHAR_HEIGHT_PX, CHAR_WIDTH_PX

import pyxel

from typing import *

class WritenText(LimitableArea, CenteredArea):
    def __init__(self, cx, cy, text: str, color: int, scale: float = 3.0, parent_surface: Optional[Surface] = None):
        self.text = text
        self.color = color
        self.background_color = 1 if color == 0 else 0
        self.scale = scale
        self.img = self.__draw_text(text, color, self.background_color)

        super().__init__(0, 0, self.img.width * scale, self.img.height * scale)
        self.to_center_pos(cx, cy)
        self.set_limiteds(parent_surface)
    
    def rewrite(self, text: str, color: int):
        self.text = text
        self.color = color
        self.background_color = 1 if color == 0 else 0
        self.img = self.__draw_text(text, color, self.background_color)

        cx, cy = self.get_center_pos()
        self.w, self.h = self.img.width * self.scale, self.img.height * self.scale
        self.to_center_pos(cx, cy)
        
    @staticmethod
    def __draw_text(text: str, color: int, background_color: int, additional_width: int = 0):
        t_w = max(0, len(text) * CHAR_WIDTH_PX - 1)
        img = pyxel.Image(t_w + additional_width, CHAR_HEIGHT_PX)
        img.cls(background_color)
        img.text(0, 0, text, color, None)
        return img

    def draw(self):
        self.drawer.blt(
            self.x + (self.scale - 1) * self.img.width / 2,
            self.y + (self.scale - 1) * self.img.height / 2,
            self.img,
            0, 0,
            self.img.width,
            self.img.height,
            colkey=self.background_color,
            scale=self.scale
        )
    
    def set_w(self, w):
        super().set_w(w)
        
        LW = 6
        
        text_max_length = min(len(self.text), (self.w - LW).__floor__() // CHAR_WIDTH_PX)
        self.img = self.__draw_text(self.text[:text_max_length], self.color, self.background_color, LW)

        leader = pyxel.Image(LW, 1)
        leader.set(0, 0, ["010101"])

        self.img.pal(1, self.color)
        self.img.blt(
            self.img.width - LW + 1, self.img.height - 1,
            leader,
            0, 0, leader.width, leader.height,
            colkey=1 
        )
        self.img.pal()
    
    def set_h(self, h):
        raise ValueError("このコンポーネントは高さを変更できない。")
