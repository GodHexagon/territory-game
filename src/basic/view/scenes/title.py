from ..view import Area, View, CenteredArea
from ..limitter import LimitableArea
from ..areas.text import WritenText
from ..text import TextDrawable
from pyxres import COLOR_PRIMARY, COLOR_BLACK, COLOR_WHITE

import pyxel

from typing import *

# タイトルのシーン
class TitleScene(Area, View):
    def __init__(self, x, y, w, h, selected_singleplay: Callable[[], None]):
        super().__init__(x, y, w, h)

        self.title = WritenText(self.x + self.w / 2, self.y + self.h / 3, "TERRITORY GAME", COLOR_BLACK, scale=5)
        self.start_button = Button(x + w / 2, y + h / 3 + 100, "START", selected_singleplay)
    
    def update(self):
        self.start_button.update()

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.title.draw()
        self.start_button.draw()
        
# 背景のあるボタン
class Button(CenteredArea, LimitableArea):
    MARGINE_PX = 6
    TEXT_SCALE = 3

    def __init__(self, cx: float, cy: float, text: str, on_click: Callable[[], None]):
        self.on_click = on_click

        self.img = TextDrawable.generate_text_image(text, 0, 1)

        super().__init__(0, 0, 
            self.img.width * Button.TEXT_SCALE + Button.MARGINE_PX * 2,
            self.img.height * Button.TEXT_SCALE + Button.MARGINE_PX * 2
        )
        self.to_center_pos(cx, cy)
        self.set_limiteds()

    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.on_click()

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)
        cx, cy = self.get_center_pos()
        self.drawer.blt(
            *TextDrawable.get_args_draw_text(self.img, cx, cy),
            scale=Button.TEXT_SCALE
        )
