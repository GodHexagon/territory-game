from .limitter import LimitableArea, LimitedDrawer
from .view import Area, View, ParenthoodView, CenteredArea
from ..rule.rule import Piece as PieceRes
from pyxres import TILE_SIZE_PX
from typing import Tuple, Dict, List
import pyxel

SLIDER_HEIGHT = 30
SLIDER_WIDTH = 30

PICKER_TILE_SCALE = 2

window_drawer: LimitedDrawer
pieces_res: Tuple[PieceRes]

class ScrollState:
    def __init__(self, value: float):
        self.value = value
    
    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))

scroll_state: ScrollState

class PickerView(LimitableArea, ParenthoodView):
    """Pickerが占有する範囲。"""
    FRAME_THICKNESS_PX = 3

    def __init__(self, x, y, w, h, pieces: Tuple[PieceRes]):
        super().__init__(x, y, w, h)

        global pieces_res
        pieces_res = pieces
        global scroll_state
        scroll_state = ScrollState(0.0)

        f = PickerView.FRAME_THICKNESS_PX
        self.set_childs( {
            "w": Window(x + f, y + f, w - f * 2, h - f * 2 - SLIDER_HEIGHT),
            "s": ScrollBar(x, y + h - SLIDER_HEIGHT + 1, w)
        } )
    
    def update(self):
        super().update()

        global scroll_state
        s = scroll_state
        s.set_value(s.value + self.input.get_wheel() * -0.1)

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 16)

        super().draw()

class Window(LimitableArea, ParenthoodView):
    """スクロール可能Viewの表示限界。"""
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.set_childs( {'s': Shelf(x, y, h)} )

        global window_drawer
        window_drawer = self.drawer
    
    def update(self):
        super().update()

        global scroll_state
        shelf: Shelf = self.childs['s']
        shelf.x = self.x + scroll_state.value * -100

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)
        super().draw()


class Shelf(Area, View):
    """スクロール可能Viewの座標系。"""
    def __init__(self, x, y, h):
        GAP_PX = 50
        width = 0
        global pieces_res

        p1: List[Piece] = []
        for i in range(len(pieces_res)):
            width += GAP_PX
            p_w_px = pieces_res[i].get_width() * TILE_SIZE_PX * PICKER_TILE_SCALE
            p1.append(Piece( (x, y), (width + p_w_px / 2, h / 2), pieces_res[i]))
            width += p_w_px
        self.pieces = tuple(p1)
        
        super().__init__(x, y, width, h)
    
    def update(self):
        for p in self.pieces: p.set_parent_pos( (self.x, self.y) )
    
    def draw(self):
        for p in self.pieces: p.draw()
        

class Piece(CenteredArea):
    """スクロール可能なピース。表示に必要な情報を持つ。"""
    def __init__(self, parent_pos: Tuple[int, int], relative_pos: Tuple[int, int], piece: PieceRes):
        self.piece = piece
        self.relative_pos = relative_pos

        s = TILE_SIZE_PX * PICKER_TILE_SCALE
        super().__init__(0, 0, piece.get_width() * s, piece.get_height() * s)

        self.set_parent_pos(parent_pos)

    def set_parent_pos(self, parent_pos: Tuple[int, int]):
        self.to_center_pos(parent_pos[0] + self.relative_pos[0], parent_pos[1] + self.relative_pos[1])
    
    def draw(self):
        global window_drawer
        window_drawer.rect(self.x, self.y, self.w, self.h, 4)

class ScrollBar(LimitableArea, View):
    """スクロールバーの範囲。"""
    def __init__(self, x, y, w):
        super().__init__(x, y, w, SLIDER_HEIGHT)
        self.slider = Slider(x, y)
        self.is_clicking = False
    
    def update(self):
        global scroll_state

        # クリック検知
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.is_clicking = True
        if self.input.btn(pyxel.MOUSE_BUTTON_LEFT) and self.is_clicking:
            scroll_state.set_value( (pyxel.mouse_x - self.x - SLIDER_WIDTH / 2) / (self.w - SLIDER_WIDTH) )
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            self.is_clicking = False
        
        self.slider.x = (self.w - SLIDER_WIDTH) * scroll_state.value

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 3)
        self.slider.draw()

class Slider(Area):
    """ScrollBarの範囲内で移動することで表示領域を示す表示。"""
    def __init__(self, x, y):
        super().__init__(x, y, SLIDER_WIDTH, SLIDER_HEIGHT)
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 2)
        for i in range(1, 4):
            x = self.x + (self.w / 4) * i
            pyxel.rect(x, self.y + self.h * 0.25, 1,self.h * 0.50, 3)
