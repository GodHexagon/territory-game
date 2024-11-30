from .limitter import LimitableArea, LimitedDrawer, LimitableArea
from .view import Area, View
from .cursor import Cursor
from ..rule.rule import Piece as PieceRes, Rotation
from ..key_bind import *

from typing import *
import numpy
import pyxel

from pyxres import TILE_SIZE_PX, BLOCK_TILE_COOR, TILE_COLOR_PALLETS_NUMBER, DEFAULT_COLOR_S
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
        self.set_limiteds()
        self.piece_color_s = color_s
        self.cursor = cursor

        global scroll_state
        scroll_state = ScrollState(0.0)

        F = PickerView.FRAME_THICKNESS_PX
        self.window = Window(self.x + F, self.y + F, self.w - F * 2, self.h - F * 2 - SLIDER_HEIGHT, self)
        self.shelf = self.window.ini_shelf()
        self.items = list(self.shelf.ini_items(pieces, color_s))
        self.scroll_bar = ScrollBar(self.x, self.y + self.h - SLIDER_HEIGHT + 1, self.w)

    def update(self):
        # スクロール検知
        global scroll_state
        scroll_state.set_value(scroll_state.value + self.input.get_wheel() * -0.1)
        self.shelf.x = self.x + PickerView.FRAME_THICKNESS_PX + scroll_state.value * -100
        
        # ピースを置く
        held_piece = self.cursor.held
        if btnp(Bind.SEIZE_PIECE) and self.window.input.is_in_range() and held_piece is not None:
            new = self.shelf.get_a_item(
                held_piece.piece,
                self.piece_color_s
            )
            target = [
                t for t in filter(lambda i: i.held is None, self.items)
            ][0]
            held_piece.follow(target)
            #self.items.append(p)
            #self.cursor.held.follow(p)

            self.shelf.align(self.items)
        else:
            # マウス操作
            for i in self.items: i.mouse_input(self.cursor)
        
        self.scroll_bar.update()

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 16)

        self.window.draw()
        s = self.shelf
        self.scroll_bar.draw()

        for p in self.items:
            #self.window.drawer.rect(p.surface.x, p.surface.y, p.surface.w, p.surface.h, 2)
            p.draw(self.piece_rotation, self.window.drawer)

    def set_piece_rotation(self, rotation: Rotation):
        self.piece_rotation = rotation

class Window(LimitableArea):
    """スクロール可能Viewの表示限界。"""
    def __init__(self, x, y, w, h, parent: PickerView):
        super().__init__(x, y, w, h)
        self.set_limiteds(parent.surface)
    
    def ini_shelf(self):
        return Shelf(self.x, self.y, self.h, self)

    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)

PICKER_TILE_SCALE = 2

class Shelf(LimitableArea):
    """スクロール可能Viewの座標系。"""
    GAP_PX = 24
    X_MARGIN_PX = 20
    
    def __init__(self, x, y, h, parent: Window):        
        super().__init__(x, y, 0, h)
        self.set_limiteds(parent.surface)
    
    def ini_items(self, pieces_res: Tuple[PieceRes], piece_color_s: int):
        width = 0
        pieces: List[Item] = []
        for p in pieces_res:
            new = self.get_a_item(p, piece_color_s)
            pieces.append(new)
            width += new.w
        self.align(pieces)
        
        return tuple(pieces)
    
    def get_a_item(self, piece_res: PieceRes, piece_color_s):
        return Item(
            self,
            (0, 0),
            piece_res,
            piece_color_s
        )

    def align(self, pieces: List['Item']):
        width = float(Shelf.X_MARGIN_PX)
        empty_items = []
        for p in pieces:
            if p.held is None:
                empty_items.append(p)
                continue
            
            p.relative_pos = (width, 0)
            p.move_absolute_pos()

            width += p.w

        width += Shelf.X_MARGIN_PX
        self.w = width
        for i in empty_items: pieces.remove(i)

from .piece import PieceHolder, FollowablePiece

class Item(LimitableArea, PieceHolder):
    def __init__(self,
        base: Shelf,
        relative_pos: Tuple[float, float],
        piece: PieceRes,
        color_s: int
    ):
        self.base = base
        self.relative_pos = relative_pos
        FollowablePiece(piece, color_s, self)

        allocation = max(
            piece.get_width_tiles() * TILE_SIZE_PX * FollowablePiece.TILE_SCALE, 
            piece.get_height_tiles() * TILE_SIZE_PX * FollowablePiece.TILE_SCALE
        )
        super().__init__(0, 0, Shelf.GAP_PX + allocation, base.h)
        self.set_limiteds(base.surface)

        self.move_absolute_pos()
    
    def move_absolute_pos(self):
        self.x = self.base.x + self.relative_pos[0]
        self.y = self.base.y + self.relative_pos[1]

    def mouse_input(self, cursor: Cursor):
        if (
            btnp(Bind.SEIZE_PIECE) and 
            self.input.is_in_range() and 
            self.held is not None and
            not cursor.is_holding()
        ):
            self.held.follow(cursor)
    
    def draw(self, piece_rotation: Rotation, drawer: LimitedDrawer):
        if self.held is not None:
            self.move_absolute_pos()
            self.held.draw(piece_rotation, drawer)

class ScrollBar(LimitableArea, View):
    """スクロールバーが占有する範囲。"""
    def __init__(self, x, y, w):
        super().__init__(x, y, w, SLIDER_HEIGHT)
        self.set_limiteds()
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
