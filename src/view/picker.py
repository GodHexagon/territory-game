from .limitter import LimitableArea
from .view import Area, Displayable, CenteredArea
from typing import Tuple
import pyxel

SLIDER_HEIGHT = 30
SLIDER_WIDTH = 30

class PickerView(Displayable, Area):
    FRAME_THICKNESS_PX = 3

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        f = self.FRAME_THICKNESS_PX
        self.childs:Tuple[Displayable] = (
            Window(x + f, y + f, w - f * 2, h - f * 2 - SLIDER_HEIGHT),
            ScrollBar(x, y + h - SLIDER_HEIGHT + 1, w)
        )
    
    def update(self):
        for c in self.childs: c.update()

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 16)

        for c in self.childs: c.draw()

class Window(Displayable, LimitableArea):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.scroll = 0.0
    
    def set_scroll(self, value: float):
        self.scroll = value
    
    def update(self):
        pass

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)

class Piece(CenteredArea):
    def __init__(self, x, y, ):
        super().__init__(x, y, 0, 0)

class ScrollBar(Displayable, LimitableArea):
    def __init__(self, x, y, w):
        super().__init__(x, y, w, SLIDER_HEIGHT)
        self.slider = Slider(x, y)
        self.value = 0.0
        self.is_clicking = False
    
    def update(self):
        # クリック検知
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.is_clicking = True
        if self.input.btn(pyxel.MOUSE_BUTTON_LEFT) and self.is_clicking:
            self.value = max(0.0, min(1.0, (pyxel.mouse_x - self.x - SLIDER_WIDTH / 2) / (self.w - SLIDER_WIDTH)))
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            self.is_clicking = False
        
        self.slider.x = (self.w - SLIDER_WIDTH) * self.value

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 3)
        self.slider.draw()

class Slider(Area):
    def __init__(self, x, y):
        super().__init__(x, y, SLIDER_WIDTH, SLIDER_HEIGHT)

    def update(self):
        pass
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 2)
        for i in range(1, 4):
            x = self.x + (self.w / 4) * i
            pyxel.rect(x, self.y + self.h * 0.25, 1,self.h * 0.50, 3)
