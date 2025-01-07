from ..base.view import Area
from .button import IconButton, TextButton
from src.pyxres import *

from typing import *

import pyxel
import pyperclip # type: ignore

class TextField(Area):
    ICON_SIZE_PX = 24
    MARGIN_PX = 8
    GAP_PX = 8
    MIN_WIDTH = 128

    def __init__(self, on_changed: Callable[[str], None], default: str = ""):
        IS = TextField.ICON_SIZE_PX
        MARGIN = TextField.MARGIN_PX

        self.on_changed = on_changed

        self.init_unplaced_area(self.MIN_WIDTH, IS + MARGIN * 2)

        TX, TY = RIGHT_ALLOW_ICON_COOR
        self.write_b = IconButton(
            0, 0, size=IS, on_click=self.__hdl_write,
            tile_selector=(TX, TY, TILE_SIZE_PX, TILE_SIZE_PX)
        )

        self.text = default
        self.field = TextButton(0, 0, lambda: None, default)
        
        TX, TY = COPY_ICON_COOR
        self.copy_b = IconButton(
            0, 0, size=IS, on_click=self.__hdl_copy,
            tile_selector=(TX, TY, TILE_SIZE_PX, TILE_SIZE_PX)
        )

        self.set_colors()
    
    def get_text(self):
        return self.text
        
    def to_x(self, x):
        diff = x - self.x
        super().to_x(x)
        self.write_b.to_x(x + self.MARGIN_PX)
        self.field.to_x(x + self.MARGIN_PX + self.ICON_SIZE_PX + self.GAP_PX)
        self.copy_b.to_x(self.copy_b.x + diff)

    def to_y(self, y):
        super().to_y(y)
        self.write_b.to_y(y + self.MARGIN_PX)
        self.field.to_y(y + ((self.MARGIN_PX * 2 + self.ICON_SIZE_PX) - self.field.h) / 2)
        self.copy_b.to_y(y + self.MARGIN_PX)
    
    def set_w(self, w):
        w = max(w, self.MIN_WIDTH)
        super().set_w(w)
        self.field.set_w(w - self.MARGIN_PX * 2 - self.ICON_SIZE_PX * 2 - self.GAP_PX * 2)
        self.copy_b.to_x(self.x + w - self.MARGIN_PX - self.ICON_SIZE_PX)
    
    def set_h(self, h):
        raise ValueError("このコンポーネントは高さを変更できない。")
    
    def set_colors(self, fill: int = COLOR_BLACK, background: int = COLOR_PRIMARY):
        self.background = background
        self.write_b.set_colors(text=fill, backgroud=background, border=background)
        self.field.set_colors(text=fill, backgroud=COLOR_WHITE, border=COLOR_WHITE)
        self.copy_b.set_colors(text=fill, backgroud=background, border=background)
        self.to_x(self.x)
        self.to_y(self.y)
        self.set_w(self.w)
    
    def __hdl_write(self):
        text: str = pyperclip.paste()
        self.text = text    
        self.on_changed(text)
        self.field.change_mode(text, lambda: None)
        self.to_x(self.x)
        self.to_y(self.y)
        self.set_w(self.w)

    def __hdl_copy(self):
        pyperclip.copy(self.text)

    def update(self):
        self.write_b.update()
        self.copy_b.update()
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, self.background)
        self.write_b.draw()
        self.field.draw()
        self.copy_b.draw()
