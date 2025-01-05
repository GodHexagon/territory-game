import pyxel

from typing import *
from abc import ABC

from src.pyxres import *
from ..view import CenteredArea
from ..limitter import LimitableArea
from .text import WritenText

class Button(CenteredArea, LimitableArea, ABC):
    def __init__(self, cx: float, cy: float, on_click: Callable[[], None]):
        self.on_click = on_click

        self.enabled = True

        super().__init__(0, 0, 0, 0)
        self.to_center_pos(cx, cy)
        self.set_colors()

        self.set_limiteds()
    
    def set_colors(self, text = COLOR_BLACK, disabled = COLOR_GRAY, backgroud = COLOR_WHITE, border = COLOR_PRIMARY):
        self.colors = (text, disabled, backgroud, border)
    
    def change_mode(self, label: str, on_click: Callable[[], None]):
        self.text = label
        self.on_click = on_click
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.enabled:
            self.on_click()

    def draw(self):
        self.drawer.rectb(self.x, self.y, self.w, self.h, self.colors[3])
        self.drawer.rect(self.x, self.y, self.w, self.h, self.colors[2])

class TextButton(Button):
    MARGIN_PX = 6

    def __init__(self, cx: float, cy: float, on_click: Callable[[], None], label: str):
        self.text = label
        self.label = WritenText(cx, cy, "", 0)
        super().__init__(cx, cy, on_click)
        self.__write_label(cx, cy)
    
    def set_colors(self, text=COLOR_BLACK, disabled=COLOR_GRAY, backgroud=COLOR_WHITE, border=COLOR_PRIMARY):
        super().set_colors(text, disabled, backgroud, border)
        self.__write_label()
    
    def change_mode(self, label, on_click):
        super().change_mode(label, on_click)
        self.__write_label()
    
    def set_enabled(self, enabled):
        super().set_enabled(enabled)
        self.__write_label()

    def __write_label(self, cx: float = None, cy: float = None) -> None:
        if cx is None or cy is None:
            cx, cy = self.get_center_pos()
        self.label = WritenText(cx, cy, self.text, color=self.colors[0] if self.enabled else self.colors[1])

        MARGIN = TextButton.MARGIN_PX
        self.w, self.h = (
            self.label.w + MARGIN * 2,
            self.label.h + MARGIN * 2
        )
        self.to_center_pos(cx, cy)
    
    def draw(self):
        super().draw()
        self.label.draw()
        
    def to_x(self, x):
        self.label.to_x(x + TextButton.MARGIN_PX)
        return super().to_x(x)
    
    def to_y(self, y):
        self.label.to_y(y + TextButton.MARGIN_PX)
        return super().to_y(y)
    
    def set_w(self, w):
        pass

    def set_h(self, h):
        pass
