from view import ViewArea
from limitter import LimitedDrawer, LimitedMouseInput
import pyxel

class BoardView(ViewArea):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.drawer = LimitedDrawer(self)
        self.input = LimitedMouseInput(self)
        self.board = ZoomableBoard(self.x + self.w // 2, self.y + self.h // 2, self.drawer)
    
    def update(self):
        if self.input.btnr(pyxel.MOUSE_BUTTON_RIGHT):
            self.dsc_mouse = None
            self.dsc_board = None
        elif self.input.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self.dsc_mouse = (pyxel.mouse_x, pyxel.mouse_y)
            self.dsc_board = self.board.get_center_coordinates()
        
        if self.input.btn(pyxel.MOUSE_BUTTON_RIGHT) and self.dsc_mouse is not None:
            self.board.to_center_coordinates(
                self.dsc_board[0] + pyxel.mouse_x - self.dsc_mouse[0],
                self.dsc_board[1] + pyxel.mouse_y - self.dsc_mouse[1]
            )
        
    
    def draw(self):
        self.board.draw()

# Game board for display
class ZoomableBoard:
    def __init__(self, cx:float, cy:float, drawer:LimitedDrawer):
        self.x = 0.0
        self.y = 0.0
        self.w = 200.0
        self.h = 200.0
        self.drawer = drawer
        self.to_center_coordinates(cx, cy)
    
    def to_center_coordinates(self, cx:float, cy:float):
        self.x = cx - self.w / 2
        self.y = cy - self.h / 2
    
    def get_center_coordinates(self):
        return (self.x + self.w / 2, self.y + self.h / 2)

    def draw(self):
        self.drawer.rect(self.x + 2, self.y + 2, self.w, self.h, 3)
        self.drawer.rect(self.x - 2, self.y - 2, self.w, self.h, 2)
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)
