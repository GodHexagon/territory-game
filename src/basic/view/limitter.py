from .view import Area
from typing import Optional
import pyxel

class LimitableArea(Area):
    def set_limiteds(self, parent_surface: Optional['Surface'] = None):
        self.surface = Surface(self, parent_surface)
        self.drawer = LimitedDrawer(self)
        self.input = LimitedMouseInput(self)

# Limitters
class LimitedMouseInput:
    def __init__(self, owner: LimitableArea):
        self.owner = owner
    
    def is_in_range(self):
        s = self.owner.surface
        s.inherit_surface()
        
        return (
            s.x <= pyxel.mouse_x and
            s.y <= pyxel.mouse_y and
            pyxel.mouse_x <= s.x + s.w and
            pyxel.mouse_y <= s.y + s.h
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
    def __init__(self, owner: LimitableArea):
        self.owner = owner

        self.blt = pyxel.blt

    def rect(self, x:float, y:float, w:float, h:float, col:int):
        s = self.owner.surface
        s.inherit_surface()
        
        pyxel.rect(
            max(s.x, x), 
            max(s.y, y), 
            (min(s.x + s.w, x + w) - max(s.x, x) + 1), 
            (min(s.y + s.h, y + h) - max(s.y, y) + 1),
            col
        )

class Surface(Area):
    def __init__(self, owner: LimitableArea, parent: Optional['Surface'] = None):
        o = owner
        super().__init__(o.x, o.y, o.w, o.h)
        self.owner = owner
        self.parent = parent
    
    def inherit_surface(self):
        p = self.parent
        o = self.owner
        if p is not None:
            p.inherit_surface()
            self.x = max(o.x, p.x)
            self.y = max(o.y, p.y)
            self.w = min(o.x + o.w, p.x + p.w) - self.x + 1
            self.h = min(o.y + o.h, p.y + p.h) - self.y + 1
        else:
            self.x = o.x
            self.y = o.y
            self.w = o.w
            self.h = o.h
