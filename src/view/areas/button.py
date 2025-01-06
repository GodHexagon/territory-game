import pyxel
from pyxel import Image

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

        super().init_area(0, 0, 0, 0)
        self.to_center_pos(cx, cy)
        self.set_colors()

        self.set_limiteds()
    
    def set_colors(self, text = COLOR_BLACK, disabled = COLOR_GRAY, backgroud = COLOR_WHITE, border = COLOR_PRIMARY):
        self.colors = (text, disabled, backgroud, border)
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.enabled:
            self.on_click()

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, self.colors[2])
        self.drawer.rectb(self.x, self.y, self.w + 1, self.h + 1, self.colors[3])

class TextButton(Button):
    MARGIN_PX = 6

    def __init__(self, cx: float, cy: float, on_click: Callable[[], None], label: str):
        self.text = label
        self.label = WritenText(cx, cy, "", 0)
        super().__init__(cx, cy, on_click)
        self.__write_label(cx, cy)
    
    def change_mode(self, label: str, on_click: Callable[[], None]):
        self.text = label
        self.on_click = on_click
        self.__write_label()

    def set_colors(self, text=COLOR_BLACK, disabled=COLOR_GRAY, backgroud=COLOR_WHITE, border=COLOR_PRIMARY):
        super().set_colors(text, disabled, backgroud, border)
        self.__write_label()
    
    def set_enabled(self, enabled):
        super().set_enabled(enabled)
        self.__write_label()

    def __write_label(self, cx: Optional[float] = None, cy: Optional[float] = None) -> None:
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
        self.label.set_w(w - self.MARGIN_PX * 2)
        return super().set_w(w)

    def set_h(self, h):
        raise ValueError("このコンポーネントは高さを変更できない。")

class IconButton(Button):
    def __init__(self, cx: float, cy: float, size: float, on_click: Callable[[], None], tile_selector: Tuple[int, int, int, int]):
        tx, ty, tw, th = tile_selector
        self.img = Image(tw, th)
        self.img.blt(0, 0, pyxel.images[0], tx, ty, tw, th)
        super().__init__(cx, cy, on_click)
        self.set_size(size)
    
    def draw(self):
        super().draw()

        pyxel.pal(0, self.colors[2])
        pyxel.pal(1, self.colors[0] if self.enabled else self.colors[1])
        pyxel.pal(2, self.colors[3])

        scale = min(self.w / self.img.width, self.h / self.img.height)
        self.drawer.blt(
            self.x + (self.w - self.img.width) / 2,
            self.y + (self.h - self.img.height) / 2,
            self.img, 0, 0, self.img.width, self.img.height,
            scale=scale
        )
        
        pyxel.pal()
    
    def set_size(self, value: float):
        pos = self.get_center_pos()
        self.w = value
        self.h = value
        self.to_center_pos(*pos)
        
    def set_w(self, w):
        raise ValueError("このコンポーネントは大きさを変えられない。set_sizeメソッドを使うべき。")

    def set_h(self, h):
        raise ValueError("このコンポーネントは大きさを変えられない。set_sizeメソッドを使うべき。")
