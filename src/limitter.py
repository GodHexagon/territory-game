from view import ViewArea
import pyxel

# Limitter
class LimitedMouseInput:
    def __init__(self, parent:ViewArea):
        self.parent = parent
    
    def enabled(self, key:int):
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
        return pyxel.btn(key) and self.enabled(key)
    
    def btnp(
        self, key: int, *, hold: int = None, repeat: int = None
    ) -> bool:
        return pyxel.btnp(key, hold=hold, repeat=repeat) and self.enabled(key)
    
    def btnr(self, key:int):
        return pyxel.btnr(key) and self.enabled(key)

class LimitedDrawer:
    def __init__(self, parent:ViewArea):
        self.parent = parent

    def rect(self, x:float, y:float, w:float, h:float, col:int):
        p = self.parent
        pyxel.rect(max(p.x, x), max(p.y, y), 
            (min(p.x + p.w, x + w) - max(p.x, x)), 
            (min(p.y + p.h, y + h) - max(p.y, y)), 
        col)