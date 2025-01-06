from ..view import Area
from .button import IconButton, TextButton
from src.pyxres import *

from typing import *

import pyxel

class TextField(Area):
    HEIGHT_PX = 24
    MARGIN_PX = 8
    GAP_PX = 8

    def __init__(self, x, y, w, on_changed: Callable[[str], None], default: str = ""):
        HEIGHT = TextField.HEIGHT_PX
        MARGIN = TextField.MARGIN_PX

        super().init_area(x, y, w, HEIGHT + MARGIN * 2)

        self.on_changed = on_changed

        self.set_colors()

        TX, TY = RIGHT_ALLOW_ICON_COOR
        self.write_b = IconButton(
            self.x + MARGIN + HEIGHT / 2, self.y + self.h / 2, size=HEIGHT, on_click=self.__hdl_write,
            tile_selector=(TX, TY, TILE_SIZE_PX, TILE_SIZE_PX)
        )
        self.write_b.set_colors(text=self.colors[0], backgroud=self.colors[1])

        self.field = TextButton(*self.get_center_pos(), lambda: None, default)
        self.field.set_colors(text=self.colors[0], backgroud=COLOR_WHITE, border=COLOR_WHITE)
        
        TX, TY = COPY_ICON_COOR
        self.copy_b = IconButton(
            self.x + self.w - MARGIN - HEIGHT / 2, self.y + self.h / 2, size=HEIGHT, on_click=self.__hdl_copy,
            tile_selector=(TX, TY, TILE_SIZE_PX, TILE_SIZE_PX)
        )
        self.copy_b.set_colors(text=self.colors[0], backgroud=self.colors[1])
    
    def set_colors(self, fill: int = COLOR_BLACK, background: int = COLOR_PRIMARY):
        self.colors = (fill, background)
    
    def __hdl_write(self):
        self.on_changed("test")
    
    def __hdl_copy(self):
        pass

    def update(self):
        self.write_b.update()
        self.copy_b.update()
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, self.colors[1])
        self.write_b.draw()
        self.field.draw()
        self.copy_b.draw()
        
    def to_x(self, x):
        raise ValueError()
    
    def to_y(self, y):
        raise ValueError()
    
    def set_w(self, w):
        raise ValueError()
    
    def set_h(self, h):
        raise ValueError()
