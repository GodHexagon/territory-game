from ...base.view import View, Area
from src.pyxres import *
from ...areas.text import WritenText
from ...areas.button import TextButton
from ...areas.textfield import TextField
from ...sequencer.access_key import AccessKeyManager

import pyxel

from typing import *
import tkinter as tk
from tkinter import messagebox

class JoiningSettingScene(View, Area):
    SIZE_PX = (500, 200)
    MARGIN_PX = 16

    def __init__(self, cx: float, cy: float,
                 on_cancel: Callable[[bool], None],
                 on_try_to_join: Callable[[str], None]) -> None:
        self.init_unplaced_area(*JoiningSettingScene.SIZE_PX)
        self.to_center_pos(cx, cy)

        self.on_cancel = on_cancel
        self.on_try_to_join = on_try_to_join

        MARGIN = JoiningSettingScene.MARGIN_PX

        self.title = WritenText(cx, 0, text="ENTER PASSWORD TO JOIN", color=COLOR_BLACK, scale=5)
        self.title.to_y(self.y + MARGIN)

        self.console = TextField(lambda _: None, "")
        self.console.set_w(self.w - MARGIN * 2)
        self.console.to_center_pos(*self.get_center_pos())

        self.try_b = TextButton(0, 0, self._hdl_try_to_join, "JOIN")
        self.try_b.set_enabled(False)
        self.try_b.set_colors(backgroud=COLOR_SUCCESSFULL)
        self.try_b.to_x_end(self.x + self.w - MARGIN)
        self.try_b.to_y_bottom(self.y + self.h - MARGIN)
        
        self.cancel_b = TextButton(0, 0, lambda : on_cancel(False), "CANCEL")
        self.cancel_b.to_x(self.x + MARGIN)
        self.cancel_b.to_y_bottom(self.y + self.h - MARGIN)
    
    def _hdl_try_to_join(self):
        self.try_b.set_enabled(False)
        self.on_try_to_join(self.console.get_text())
    
    def allowed_to_access(self):
        self.try_b.set_enabled(True)
    
    def get_password(self):
        return self.console.get_text()
    
    def update(self):
        if isinstance(self.console, TextField):
            self.console.update()
        self.try_b.update()
        self.cancel_b.update()
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.title.draw()
        self.console.draw()
        self.try_b.draw()
        self.cancel_b.draw()
