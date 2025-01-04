import pyxel

from typing import *

from src.pyxres import *
from ..view import CenteredArea
from ..limitter import LimitableArea
from .text import WritenText

class Button(CenteredArea, LimitableArea):
    MARGIN_PX = 6
    
    def __init__(self, cx: float, cy: float, label: str, on_click: Callable[[], None]):
        self.text = label
        self.on_click = on_click
        self.set_colors()

        self.enabled = True

        super().__init__(0, 0, 0, 0)
        self.__write_label(cx, cy)

        self.set_limiteds()
    
    def set_colors(self, text = COLOR_BLACK, disabled = COLOR_GRAY, backgroud = COLOR_WHITE, border = COLOR_PRIMARY):
        self.colors = (text, disabled, backgroud, border)
    
    def chage_mode(self, label: str, on_click: Callable[[], None]):
        self.text = label
        self.on_click = on_click
        
        self.__write_label(*self.get_center_pos())
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        self.__write_label(
            *self.get_center_pos()
        )
        
    def __write_label(self, cx: float, cy: float) -> None:
        self.label = WritenText(cx, cy, self.text, self.colors[0] if self.enabled else self.colors[1])

        MARGIN = Button.MARGIN_PX
        self.w, self.h = (
            self.label.w + MARGIN * 2,
            self.label.h + MARGIN * 2
        )
        self.to_center_pos(cx, cy)
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.enabled:
            self.on_click()

    def draw(self):
        self.drawer.rectb(self.x, self.y, self.w, self.h, self.colors[3])
        self.drawer.rect(self.x, self.y, self.w, self.h, self.colors[2])
        self.label.draw()
    
    def to_x(self, x):
        self.label.to_x(x + Button.MARGIN_PX)
        return super().to_x(x)
    
    def to_y(self, x):
        self.label.to_y(x + Button.MARGIN_PX)
        return super().to_y(x)
    
    def set_w(self, w):
        pass

    def set_h(self, h):
        pass
