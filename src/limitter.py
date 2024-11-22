from view import Area
from typing import Optional
import pyxel

class LimitableArea(Area):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.drawer = LimitedDrawer(self)
        self.input = LimitedMouseInput(self)

# Limitter
class LimitedMouseInput:
    def __init__(self, parent:Area):
        self.parent = parent
    
    def __enabled(self, key:int):
        mbs = (
            pyxel.MOUSE_BUTTON_LEFT,
            pyxel.MOUSE_BUTTON_RIGHT,
            pyxel.MOUSE_BUTTON_MIDDLE,
            pyxel.MOUSE_BUTTON_X1,
            pyxel.MOUSE_BUTTON_X2,
            pyxel.MOUSE_POS_X,
            pyxel.MOUSE_POS_Y,
            pyxel.MOUSE_WHEEL_X,
            pyxel.MOUSE_WHEEL_Y
        )
        p = self.parent
        return key not in mbs or (
            p.x <= pyxel.mouse_x and
            p.y <= pyxel.mouse_y and
            pyxel.mouse_x <= p.x + p.w and
            pyxel.mouse_y <= p.y + p.h
        )
    
    def btn(self, key:int):
        return pyxel.btn(key) and self.__enabled(key)
    
    def btnp(
        self, key: int, *, hold: Optional[int] = None, repeat: Optional[int] = None
    ) -> bool:
        return pyxel.btnp(key, hold=hold, repeat=repeat) and self.__enabled(key)
    
    def btnr(self, key:int):
        return pyxel.btnr(key) and self.__enabled(key)

class LimitedDrawer:
    def __init__(self, parent:Area):
        self.parent = parent

        self.lblt = pyxel.blt

    def rect(self, x:float, y:float, w:float, h:float, col:int):
        p = self.parent
        pyxel.rect(max(p.x, x), max(p.y, y), 
            (min(p.x + p.w, x + w) - max(p.x, x) + 1), 
            (min(p.y + p.h, y + h) - max(p.y, y) + 1), 
        col)