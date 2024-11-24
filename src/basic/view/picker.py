from .limitter import LimitableArea, LimitedDrawer
from .view import Area, View, ParenthoodView, CenteredArea
from ..rule.rule import Piece as PieceRes, Rotation
from typing import Tuple, Dict, List
import numpy
import pyxel

from pyxres import TILE_SIZE_PX, BLOCK_TILE_COOR, TILE_COLOR_PALLET_NUMBER, DEFAULT_COLOR_S
SLIDER_HEIGHT = 30
SLIDER_WIDTH = 30

PICKER_TILE_SCALE = 2

window_drawer: LimitedDrawer
pieces_res: Tuple[PieceRes]
piece_rotation: Rotation
piece_color_s: int

class ScrollState:
    def __init__(self, value: float):
        self.value = value
    
    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))

scroll_state: ScrollState

class PickerView(LimitableArea, ParenthoodView):
    """Pickerが占有する範囲。"""
    FRAME_THICKNESS_PX = 3

    def __init__(self, x, y, w, h, pieces: Tuple[PieceRes], color_s: int):
        super().__init__(x, y, w, h)

        global pieces_res
        pieces_res = pieces
        global scroll_state
        scroll_state = ScrollState(0.0)
        global piece_rotation
        piece_rotation = Rotation.DEFAULT
        global piece_color_s
        piece_color_s = color_s

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

    def set_piece_rotation(self, rotation: Rotation):
        global piece_rotation
        piece_rotation = rotation

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

        pieces: List[Piece] = []
        for p in pieces_res:
            image = pyxel.Image(p.get_width() * TILE_SIZE_PX, p.get_height() * TILE_SIZE_PX)
            global piece_color_s
            for i in range(TILE_COLOR_PALLET_NUMBER): image.pal(i + DEFAULT_COLOR_S, i + piece_color_s)
            for (row, col), value in numpy.ndenumerate(p.shape):
                if value == PieceRes.TILED:
                    image.blt(
                        col * TILE_SIZE_PX,
                        row * TILE_SIZE_PX,
                        pyxel.image(0),
                        BLOCK_TILE_COOR[0], 
                        BLOCK_TILE_COOR[1], 
                        TILE_SIZE_PX,
                        TILE_SIZE_PX,
                    )
                    
            p_w_px = p.get_width() * TILE_SIZE_PX * PICKER_TILE_SCALE
            p_h_px = p.get_height() * TILE_SIZE_PX * PICKER_TILE_SCALE
            
            """
            scaled = pyxel.Image(p_w_px, p_h_px)
            scaled.blt((PICKER_TILE_SCALE - 1) * p_w_px / 2, 
                       (PICKER_TILE_SCALE - 1) * p_h_px / 2, 
                       image, 0, 0, image.width, image.height, scale=PICKER_TILE_SCALE)
            """

            width += GAP_PX
            pieces.append(Piece(
                (x, y), 
                (width + p_w_px / 2, h / 2),
                p_w_px,
                p_h_px,
                image
            ))
            width += p_w_px
        self.pieces = tuple(pieces)
        
        super().__init__(x, y, width, h)
    
    def update(self):
        for p in self.pieces: p.set_parent_pos( (self.x, self.y) )
    
    def draw(self):
        for p in self.pieces: p.draw()
        

class Piece(LimitableArea, CenteredArea):
    """スクロール可能なピース。表示に必要な情報を持つ。"""
    def __init__(self,
        parent_pos: Tuple[int, int], 
        relative_pos: Tuple[int, int],
        width: int,
        height: int,
        image: pyxel.Image
    ):
        self.relative_pos = relative_pos
        self.image = image

        super().__init__(0, 0, width, height)
        self.set_parent_pos(parent_pos)

    def set_parent_pos(self, parent_pos: Tuple[int, int]):
        self.to_center_pos(parent_pos[0] + self.relative_pos[0], parent_pos[1] + self.relative_pos[1])
    
    def draw(self):
        global piece_rotation
        if piece_rotation == Rotation.RIGHT_90:
            dagree = -90
        elif piece_rotation == Rotation.RIGHT_180:
            dagree = -180
        elif piece_rotation == Rotation.RIGHT_270:
            dagree = -270
        else:
            dagree = 0

        global window_drawer
        window_drawer.lblt(
            self.x,
            self.y,
            self.image,
            0, 0, self.image.width, self.image.height,
            colkey=0,
            rotate=dagree,
            scale=PICKER_TILE_SCALE
        )

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
