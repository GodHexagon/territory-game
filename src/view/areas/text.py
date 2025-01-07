from ..base.view import CenteredArea
from ..base.limitter import LimitableArea, Surface
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

        super().init_area(0, 0, self.img.width * scale, self.img.height * scale)
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

        if len(self.text) > self.w.__floor__() // (CHAR_WIDTH_PX * self.scale).__floor__():
            display_length = (self.w - LW).__floor__() // (CHAR_WIDTH_PX * self.scale).__floor__()
        else:
            display_length = None
        
        self.img = self.__draw_text(
            self.text[:display_length if display_length is not None else len(self.text)],
            self.color, 
            self.background_color, 
            LW
        )

        if display_length is not None:
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
