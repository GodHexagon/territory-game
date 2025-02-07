from ..limitter import LimitableArea, LimitedDrawer, LimitableArea
from ..view import Area, View
from .cursor import Cursor
from ...rule.rule import TilesMap, Rotation
from ...key_bind import *

from typing import *
import numpy
import pyxel

from src.pyxres import TILE_SIZE_PX, BLOCK_TILE_COOR, TILE_COLOR_PALLETS_NUMBER, DEFAULT_COLOR_S
SLIDER_HEIGHT = 30
SLIDER_WIDTH = 30

class ScrollState:
    def __init__(self, value: float, range_px: int):
        self.set_value(value)
        self.set_range_px(range_px)
    
    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))
    
    def set_range_px(self, value: int):
        self.range_px = max(0, value)
        self.enable = self.range_px > 0
    
    def scroll_by_px(self, px: int):
        if not self.enable: return
        self.set_value(self.value + px / self.range_px)
    
    def get_scrolled_px(self):
        return self.value * self.range_px

scroll_state: ScrollState

class PickerView(LimitableArea, View):
    """Pickerが占有する範囲。"""
    FRAME_THICKNESS_PX = 3

    def __init__(self, x, y, w, h, pieces: Tuple[TilesMap], color_s: int, cursor: Cursor):
        super().__init__(x, y, w, h)
        self.set_limiteds()
        self.piece_color_s = color_s
        self.cursor = cursor

        global scroll_state
        scroll_state = ScrollState(0.0, 0)

        F = PickerView.FRAME_THICKNESS_PX
        self.window = Window(self.x + F, self.y + F, self.w - F * 2, self.h - F * 2 - SLIDER_HEIGHT, self)
        self.shelf = self.window.ini_shelf()
        self.reset_pieces(pieces)
        self.scroll_bar = ScrollBar(self.x, self.y + self.h - SLIDER_HEIGHT + 1, self.w)
    
    def reset_pieces(self, pieces: Tuple[TilesMap, ...]) -> None:
        self.items = list(self.shelf.ini_items(
            pieces,
            self.piece_color_s
        ))
        global scroll_state
        scroll_state.set_range_px(self.shelf.w - self.window.w)

    def update(self):
        # スクロール検知
        global scroll_state
        scroll_state.scroll_by_px(self.input.get_wheel() * -100)
        self.shelf.x = self.window.x - scroll_state.get_scrolled_px()
        
        # ピースを置く
        held_piece = self.cursor.held
        if btnp(Bind.SEIZE_PIECE) and self.window.input.is_in_range() and held_piece is not None:
            target = [
                t for t in filter(lambda i: i.held is None, self.items)
            ][0]
            held_piece.follow(target)

            self.shelf.align(self.items)
            scroll_state.set_range_px(self.shelf.w - self.window.w)
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
    GAP_PX = 16
    X_MARGIN_PX = 20
    
    def __init__(self, x, y, h, parent: Window):        
        super().__init__(x, y, 0, h)
        self.set_limiteds(parent.surface)
    
    def ini_items(self, pieces_res: Tuple[TilesMap], piece_color_s: int):
        width = 0
        pieces: List[Item] = []
        for p in pieces_res:
            new = self.get_a_item(p, piece_color_s)
            pieces.append(new)
            width += new.w
        self.align(pieces)
        
        return tuple(pieces)
    
    def get_a_item(self, piece_res: TilesMap, piece_color_s: int):
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
            
            p.relative_pos = (width, 0.0)
            p.resize_w()
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
        piece: TilesMap,
        color_s: int
    ):
        self.base = base
        self.relative_pos = relative_pos
        FollowablePiece(piece, color_s, self)

        super().__init__(0, 0, 0, base.h)

        self.set_limiteds(base.surface)
        self.resize_w()
        self.move_absolute_pos()
    
    def resize_w(self):
        if self.held is None: return False
        
        self.w = Shelf.GAP_PX + max(
            self.held.shape.width * TILE_SIZE_PX * FollowablePiece.TILE_SCALE, 
            self.held.shape.height * TILE_SIZE_PX * FollowablePiece.TILE_SCALE
        )
        return True
    
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
        self.drawer.rect(self.x + 1, self.y + 1, self.w - 1, self.h - 1, 3)
        global scroll_state
        if scroll_state.enable:
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
