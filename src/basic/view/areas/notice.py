from ..view import Area, View

import pyxel

from typing import *

class FrontNoticeView(Area, View):
    FADE_OUT_TIME_FRAME = 30
    BORDER_THICKNESS_PX = 5

    from pyxres import CHAR_HEIGHT_PX, CHAR_WIDTH_PX

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.__set_text('', 0)
        self.hidden_time = pyxel.frame_count
        self.transparent = 0.0
    
    def put(self, text: str, color: int = 0, frame_to_hide: int = 180):
        self.__set_text(text, color)
        self.hidden_time = pyxel.frame_count + frame_to_hide
        self.transparent = 1.0
    
    def __set_text(self, value: str, color: int):
        self.t_w = max(0, len(value) * FrontNoticeView.CHAR_WIDTH_PX - 1)
        img = pyxel.Image(self.t_w, FrontNoticeView.CHAR_HEIGHT_PX)
        img.cls(1)
        img.text(0, 0, value, color, None)
        self.text = img
    
    def update(self):
        now = pyxel.frame_count
        fadeout = FrontNoticeView.FADE_OUT_TIME_FRAME
        self.transparent = max(0.0, min(1.0, self.hidden_time / fadeout - now / fadeout + 1))
    
    def draw(self):
        now = pyxel.frame_count
        fadeout = FrontNoticeView.FADE_OUT_TIME_FRAME
        border = FrontNoticeView.BORDER_THICKNESS_PX
        if now - self.hidden_time - fadeout < 0:
            pyxel.dither(self.transparent)
            pyxel.rect(self.x, self.y, self.w, self.h, 16)
            pyxel.rect(self.x + border, self.y + border, self.w - border * 2, self.h - border * 2, 1)
            pyxel.blt(
                self.x + (self.w - self.t_w) / 2,
                self.y + (self.h - FrontNoticeView.CHAR_HEIGHT_PX) / 2,
                self.text,
                0, 0,
                self.t_w,
                FrontNoticeView.CHAR_HEIGHT_PX,
                colkey=1,
                scale=3
            )
            pyxel.dither(1.0)
