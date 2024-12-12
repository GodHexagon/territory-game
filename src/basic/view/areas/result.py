from ..view import Area, View
from pyxres import *

import pyxel
from pyxel import Image

from typing import *

class ResultWindow(Area, View):
    BORDER_THICKNESS_PX = 5

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.title = self.__get_typo_image('DRAW', 0)
        self.text_imgs: List[Image] | None = None
    
    def show(self, rows: List[Tuple[str, int]], win: int):
        imgs: List[Image] = []
        for text, color in rows:
            imgs.append(self.__get_typo_image(text, color))
        self.text_imgs = imgs

        if win == 1: self.title = self.__get_typo_image("VICTORY!", COLOR_SUCCESSFULL)
        elif win == -1: self.title = self.__get_typo_image("DEFEAT", COLOR_FAILURE)
    
    def __get_typo_image(self, text: str, color: int):
        t_w = max(0, len(text) * CHAR_WIDTH_PX - 1)
        img = Image(t_w, CHAR_HEIGHT_PX)
        img.cls(1)
        img.text(0, 0, text, color, None)
        return img
    
    def update(self):
        pass

    def draw(self):
        if self.text_imgs is not None:
            border = ResultWindow.BORDER_THICKNESS_PX
            pyxel.rect(self.x, self.y, self.w, self.h, 16)
            pyxel.rect(self.x + border, self.y + border, self.w - border * 2, self.h - border * 2, 1)
            pyxel.blt(
                self.x + (self.w - self.title.width) / 2,
                self.y + 30,
                self.title,
                0, 0, self.title.width, self.title.height,
                colkey=1,
                scale=4
            )
            for image, i in zip(self.text_imgs, range(self.text_imgs.__len__())):
                pyxel.blt(
                    self.x + 50,
                    self.y + 60 + 30 * i,
                    image,
                    0, 0, image.width, image.height,
                    colkey=1,
                    scale=3
                )
