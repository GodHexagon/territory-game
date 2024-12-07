from ..view import Area, View
from pyxres import CHAR_HEIGHT_PX, CHAR_WIDTH_PX

import pyxel
from pyxel import Image

from typing import *

class VSAIResultView(Area, View):
    BORDER_THICKNESS_PX = 5

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.title = self.__get_typo_image('RESULT', 0)
        self.scores: Tuple[Image, Image] | None = None
    
    def show(self, scores: Tuple[int, int], colors: Tuple[int, int], win: bool):
        self.scores = (self.__get_typo_image(f"YOU: {scores[0]}", colors[0]), self.__get_typo_image(f"ENEMY: {scores[1]}", colors[1]))

        from pyxres import COLOR_SUCCESSFULL, COLOR_FAILURE
        if win: self.title = self.__get_typo_image("VICTORY!", COLOR_SUCCESSFULL)
        else: self.title = self.__get_typo_image("DEFEAT", COLOR_FAILURE)
    
    def __get_typo_image(self, value: str, color: int):
        self.t_w = max(0, len(value) * CHAR_WIDTH_PX - 1)
        img = Image(self.t_w, CHAR_HEIGHT_PX)
        img.cls(1)
        img.text(0, 0, value, color, None)
        return img
    
    def update(self):
        pass

    def draw(self):
        if self.scores is not None:
            border = VSAIResultView.BORDER_THICKNESS_PX
            pyxel.rect(self.x, self.y, self.w, self.h, 16)
            pyxel.rect(self.x + border, self.y + border, self.w - border * 2, self.h - border * 2, 1)
            pyxel.blt(
                self.x + (self.w - self.t_w) / 2,
                self.y + 30,
                self.title,
                0, 0, self.title.width, self.title.height,
                colkey=1,
                scale=4
            )
            p, e = self.scores
            pyxel.blt(
                self.x + 50,
                self.y + 60,
                p,
                0, 0, p.width, p.height,
                colkey=1,
                scale=3
            )
            pyxel.blt(
                self.x + 50,
                self.y + 90,
                e,
                0, 0, e.width, e.height,
                colkey=1,
                scale=3
            )
