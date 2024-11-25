from .limitter import LimitableArea, LimitedDrawer
from .view import Area, View, ParenthoodView, CenteredArea
from .cursor import Cursor, Followable
from ..rule.rule import Piece as PieceRes, Rotation
from ..key_bind import *

from typing import *
import numpy
import pyxel

from pyxres import TILE_SIZE_PX, BLOCK_TILE_COOR, TILE_COLOR_PALLET_NUMBER, DEFAULT_COLOR_S
SLIDER_HEIGHT = 30
SLIDER_WIDTH = 30

class ScrollState:
    def __init__(self, value: float):
        self.value = value
    
    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))

scroll_state: ScrollState

class PickerView(LimitableArea, View):
    """Pickerが占有する範囲。"""
    FRAME_THICKNESS_PX = 3

    def __init__(self, x, y, w, h, pieces: Tuple[PieceRes], color_s: int, cursor: Cursor):
        super().__init__(x, y, w, h)
        self.cursor = cursor

        global scroll_state
        scroll_state = ScrollState(0.0)

        F = PickerView.FRAME_THICKNESS_PX
        self.window = Window(self.x + F, self.y + F, self.w - F * 2, self.h - F * 2 - SLIDER_HEIGHT)
        self.shelf = self.window.ini_shelf()
        self.pieces = self.shelf.ini_pieces(pieces, color_s)
        self.scroll_bar = ScrollBar(self.x, self.y + self.h - SLIDER_HEIGHT + 1, self.w)

    def update(self):
        # スクロール検知
        global scroll_state
        scroll_state.set_value(scroll_state.value + self.input.get_wheel() * -0.1)
        self.shelf.x = self.x + scroll_state.value * -100
        
        # ピースを置く
        if btnp(Bind.SEIZE_PIECE) and self.window.input.is_in_range() and self.cursor.is_holding():
            self.cursor.hold()
            self.shelf.align(self.pieces)

        # updates
        self.scroll_bar.update()
        for p in self.pieces: p.update(self.cursor)

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 16)

        self.window.draw()
        s = self.shelf
        pyxel.rect(s.x, s.y, s.w, s.h, 2)
        self.scroll_bar.draw()
        for p in self.pieces: p.draw(self.piece_rotation, self.window.drawer)

    def set_piece_rotation(self, rotation: Rotation):
        self.piece_rotation = rotation

class Window(LimitableArea):
    """スクロール可能Viewの表示限界。"""
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
    
    def ini_shelf(self):
        return Shelf(self.x, self.y, self.h)

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)

PICKER_TILE_SCALE = 2

class Shelf(Area):
    """スクロール可能Viewの座標系。"""
    GAP_PX = 48
    
    def __init__(self, x, y, h):        
        super().__init__(x, y, 0, h)
    
    def ini_pieces(self, pieces_res: Tuple[PieceRes], piece_color_s: int):
        width = 0
        pieces: List[Piece] = []
        for p in pieces_res:
            # 画像を生成
            image = pyxel.Image(p.get_width() * TILE_SIZE_PX, p.get_height() * TILE_SIZE_PX)
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
            
            # インスタンス化
            p_w_px = p.get_width() * TILE_SIZE_PX * PICKER_TILE_SCALE
            p_h_px = p.get_height() * TILE_SIZE_PX * PICKER_TILE_SCALE

            width += Shelf.GAP_PX
            pieces.append(Piece(
                self,
                (width + p_w_px / 2, self.h / 2),
                p_w_px,
                p_h_px,
                image
            ))
        
        self.align(pieces)
        return tuple(pieces) 

    def align(self, pieces: Tuple['Piece']):
        width = 0
        for p in pieces:
            width += Shelf.GAP_PX
            
            width += p.allocated / 2
            p.follow(self, (width, self.h / 2))
            width += p.allocated / 2
        width += Shelf.GAP_PX
        self.w = width

class Piece(LimitableArea, CenteredArea, Followable):
    """スクロール可能なピース。表示に必要な情報を持つ。"""

    def __init__(self,
        parent: Area,
        relative_pos: Tuple[int, int],
        width: int,
        height: int,
        image: pyxel.Image
    ):
        self.follow(parent, relative_pos)
        self.set_visibility(True)
        self.image = image

        super().__init__(0, 0, width, height)
        
        self.allocated = max(self.w, self.h)
    
    def follow(self, to: Area, relative_pos: Tuple[int, int] = (0, 0)):
        self.relative_pos = relative_pos
        self.following_to = to
    
    def update(self, cursor: Cursor):
        self.to_center_pos(self.following_to.x + self.relative_pos[0], self.following_to.y + self.relative_pos[1])

        if btnp(Bind.SEIZE_PIECE) and self.input.is_in_range() and not cursor.is_holding():
            cursor.hold(self)
    
    def draw(self, piece_rotation: Rotation, drawer: LimitedDrawer):
        if piece_rotation == Rotation.RIGHT_90:
            dagree = -90
        elif piece_rotation == Rotation.RIGHT_180:
            dagree = -180
        elif piece_rotation == Rotation.RIGHT_270:
            dagree = -270
        else:
            dagree = 0

        T = PICKER_TILE_SCALE
        drawer.lblt(
            self.x + (T - 1) * (self.image.width / 2),
            self.y + (T - 1) * (self.image.height / 2),
            self.image,
            0, 0, self.image.width, self.image.height,
            colkey=0,
            rotate=dagree,
            scale=T
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
