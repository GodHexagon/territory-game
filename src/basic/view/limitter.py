from .view import Area
from typing import Optional
import pyxel

class LimitableArea(Area):
    def set_limiteds(self):
        self.drawer = LimitedDrawer(self)
        self.input = LimitedMouseInput(self)

# Limitter
class LimitedMouseInput:
    def __init__(self, parent:Area):
        self.parent = parent
    
    def is_in_range(self):
        p = self.parent
        return (
            p.x <= pyxel.mouse_x and
            p.y <= pyxel.mouse_y and
            pyxel.mouse_x <= p.x + p.w and
            pyxel.mouse_y <= p.y + p.h
        )
    
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
        return key not in mbs or self.is_in_range()
    
    def btn(self, key:int):
        return pyxel.btn(key) and self.__enabled(key)
    
    def btnp(
        self, key: int, *, hold: Optional[int] = None, repeat: Optional[int] = None
    ) -> bool:
        return pyxel.btnp(key, hold=hold, repeat=repeat) and self.__enabled(key)
    
    def btnr(self, key:int):
        return pyxel.btnr(key) and self.__enabled(key)
    
    def get_wheel(self):
        m = 1 if self.is_in_range() else 0
        return pyxel.mouse_wheel * m

class LimitedDrawer:
    def __init__(self, owner :Area):
        self.owner = owner

        self.blt = pyxel.blt

    def rect(self, x:float, y:float, w:float, h:float, col:int):
        o = self.owner
        pyxel.rect(max(o.x, x), max(o.y, y), 
            (min(o.x + o.w, x + w) - max(o.x, x) + 1), 
            (min(o.y + o.h, y + h) - max(o.y, y) + 1),
        col)

class Surface(Area):
    def __init__(self, x, y, w, h, owner: LimitableArea, parent: Optional['Surface'] = None):
        super().__init__(x, y, w, h)
        self.owner = owner
        self.parent = parent
    
    def inherit_surface(self):
        p = self.parent
        o = self.owner
        if p is not None:
            p.inherit_surface()
        self.x = max(o.x, p.x)
        self.y = max(o.y, p.y)
        self.w = min(o.x + o.w, p.x + p.w)
        self.w = min(o.y + o.h, p.y + p.h)
