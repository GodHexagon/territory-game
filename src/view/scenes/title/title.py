from ...base.view import Area, View
from ...areas.button import TextButton
from ...areas.text import WritenText
from src.pyxres import COLOR_PRIMARY, COLOR_BLACK, COLOR_WHITE

import pyxel

from typing import *

# タイトルのシーン
class TitleScene(Area, View):
    def __init__(self, x, y, w, h, 
            on_singleplayer_selected: Callable[[], None], 
            on_multiplayer_selected: Callable[[], None],
            on_akst_selected: Callable[[], None]
        ):
        super().init_area(x, y, w, h)

        self.title = WritenText(self.x + self.w / 2, self.y + self.h / 3, "TERRITORY GAME", COLOR_BLACK, scale=5)
        self.sp_button = TextButton(x + w / 2, y + h / 3 + 100, on_singleplayer_selected, "SINGLEPLAY")
        self.mp_button = TextButton(x + w / 2, y + h / 3 + 164, on_multiplayer_selected, "MULTIPLAY")
        self.akst_button = TextButton(x + w / 2, y + h / 3 + 228, on_akst_selected, "SET ACCESS KEY")
    
    def update(self):
        self.sp_button.update()
        self.mp_button.update()
        self.akst_button.update()

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.title.draw()
        self.sp_button.draw()
        self.mp_button.draw()
        self.akst_button.draw()
