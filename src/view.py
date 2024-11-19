from abc import ABC, abstractmethod
import pyxel

# ViewAreas
class ViewArea(ABC):
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class BoardView(ViewArea):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.drawer = LimitedDrawer(self)
        self.input = LimitedMouseInput(self)
        self.board = ZoomableBoard(self.x + self.w // 2, self.y + self.h // 2, self.drawer)
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            
        if self.input.btn(pyxel.MOUSE_BUTTON_RIGHT):
            self.board.to_center_coordinates(pyxel.mouse_x, pyxel.mouse_y)
    
    def draw(self):
        self.board.draw()

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
    
    def btnp(self, key:int):
        return pyxel.btnp(key) and self.enabled(key)

class LimitedDrawer:
    def __init__(self, parent:ViewArea):
        self.parent = parent

    def rect(self, x:float, y:float, w:float, h:float, col:int):
        p = self.parent
        pyxel.rect(max(p.x, x), max(p.y, y), 
            (min(p.x + p.w, x + w) - max(p.x, x)), 
            (min(p.y + p.h, y + h) - max(p.y, y)), 
        col)

# Game board for display
class ZoomableBoard:
    def __init__(self, cx:float, cy:float, drawer:LimitedDrawer):
        self.x = 0
        self.y = 0
        self.w = 200
        self.h = 200
        self.drawer = drawer
        self.to_center_coordinates(cx, cy)
    
    def to_center_coordinates(self, cx, cy):
        self.x = cx - self.w // 2
        self.y = cy - self.h // 2

    def draw(self):
        self.drawer.rect(self.x + 2, self.y + 2, self.w, self.h, 3)
        self.drawer.rect(self.x - 2, self.y - 2, self.w, self.h, 2)
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)
