from limitter import LimitableView
from view import ViewArea
from typing import Tuple
import pyxel

SCROLLBAR_HEIGHT = 30

class PickerView(ViewArea):
    FRAME_THICKNESS_PX = 3

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        f = self.FRAME_THICKNESS_PX
        self.childs:Tuple[ViewArea] = (
            ScrollableWindow(x + f, y + f, w - f * 2, h - f * 2 - SCROLLBAR_HEIGHT),
            ScrollBar(x, y, w)
        )
    
    def update(self):
        for c in self.childs: c.update()

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 16)

        for c in self.childs: c.draw()

class ScrollableWindow(LimitableView):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
    
    def update(self):
        pass

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)

class ScrollBar(LimitableView):
    def __init__(self, x, y, w):
        super().__init__(x, y, w, SCROLLBAR_HEIGHT)
    
    def update(self):
        pass

    def draw(self):
        pass
