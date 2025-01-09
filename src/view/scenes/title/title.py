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
            on_selected_host: Callable[[], None],
            on_selected_join: Callable[[], None],
            on_akst_selected: Callable[[], None]
        ):
        super().init_area(x, y, w, h)

        self.title = WritenText(self.x + self.w / 2, self.y + self.h / 3, "TERRITORY GAME", COLOR_BLACK, scale=5)
        self.sp_button = TextButton(x + w / 2, y + h / 3 + 100, on_singleplayer_selected, "SINGLEPLAY")
        self.host_button = TextButton(x + w / 2, y + h / 3 + 164, on_selected_host, "HOST ON SERVER")
        self.join_button = TextButton(x + w / 2, y + h / 3 + 228, on_selected_join, "JOIN TO GAME")
        self.akst_button = TextButton(x + w / 2, y + h / 3 + 292, on_akst_selected, "SET ACCESS KEY")
    
    def update(self):
        self.sp_button.update()
        self.host_button.update()
        self.join_button.update()
        self.akst_button.update()

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.title.draw()
        self.sp_button.draw()
        self.host_button.draw()
        self.join_button.draw()
        self.akst_button.draw()
