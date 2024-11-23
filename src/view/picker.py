from .limitter import LimitableArea
from .view import Area, View, ParenthoodView, CenteredArea
from typing import Tuple, Dict
import pyxel

SLIDER_HEIGHT = 30
SLIDER_WIDTH = 30

class PickerView(LimitableArea, ParenthoodView):
    FRAME_THICKNESS_PX = 3

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        f = PickerView.FRAME_THICKNESS_PX
        self.childs: Dict[str, View] = {
            "w": Window(x + f, y + f, w - f * 2, h - f * 2 - SLIDER_HEIGHT),
            "s": ScrollBar(x, y + h - SLIDER_HEIGHT + 1, w)
        }
    
    def update(self):
        super().update()
        s: ScrollBar = self.childs["s"]
        s.set_scroll(s.value + self.input.get_wheel() * 0.1)

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 16)

        super().draw()

class Window(View, LimitableArea):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.scroll = 0.0
    
    def set_scroll(self, value: float):
        self.scroll = value
    
    def update(self):
        pass

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)

class Shelf(Area):
    def __init__(self, x, y, h, peices: Tuple):
        pass
        

class Piece(CenteredArea):
    def __init__(self, cx, cy, shape: Tuple[Tuple[int]]):
        self.shape = shape
        super().__init__(0, 0, 0, 0)
        self.to_center_pos(cx, cy)

class ScrollBar(View, LimitableArea):
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
            self.set_scroll( (pyxel.mouse_x - self.x - SLIDER_WIDTH / 2) / (self.w - SLIDER_WIDTH) )
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            self.is_clicking = False
        
        self.slider.x = (self.w - SLIDER_WIDTH) * self.value
    
    def set_scroll(self, value: float):
        self.value = max(0.0, min(1.0, value))

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 3)
        self.slider.draw()

class Slider(Area):
    def __init__(self, x, y):
        super().__init__(x, y, SLIDER_WIDTH, SLIDER_HEIGHT)
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 2)
        for i in range(1, 4):
            x = self.x + (self.w / 4) * i
            pyxel.rect(x, self.y + self.h * 0.25, 1,self.h * 0.50, 3)
