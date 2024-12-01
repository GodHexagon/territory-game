from .limitter import LimitableArea, LimitedDrawer, Surface
from .view import View, CenteredArea
from .cursor import Cursor
from ..rule.rule import Rotation, TilesMap, Rule, Piece
from ..key_bind import Bind, btn, btnp

from typing import *

import pyxel
from numpy import ndarray as NDArray
import numpy

from pyxres import DEFAULT_COLOR_S, RED_COLOR_S, BLUE_COLOR_S



class BoardView(View, LimitableArea):
    """DraggableBoardの表示限界。"""
    DRAGGABLE_LIMIT_POCKET_PX = 50
    DRAG = pyxel.MOUSE_BUTTON_RIGHT
    
    TILE_COLORS = (DEFAULT_COLOR_S, BLUE_COLOR_S, RED_COLOR_S)

    def __init__(self, x, y, w, h, cursor: Cursor, colors_s: int, game: Rule):
        super().__init__(x, y, w, h)
        self.set_limiteds()

        self.commited_tiles_data = numpy.array( [[0 for _ in range(DraggableBoard.BOARD_SIZE_TILES)] for _ in range(DraggableBoard.BOARD_SIZE_TILES)] )
        self.displaying_tiles_data = self.commited_tiles_data

        self.board = DraggableBoard(
            self.x + self.w // 2, 
            self.y + self.h // 2, 
            self.drawer, 
            self.__draw_tiles(self.displaying_tiles_data)
        )

        self.c_monitor = self.board.ini_b_input(self, cursor)
        self.color_s = colors_s
        self.game = game
        self.dg: Dragging | None = None
    
    def set_piece_rotation(self, value: Rotation):
        self.piece_rotation = value
    
    def update(self):
        # ドラッグ検知・計算
        if pyxel.btnr(self.DRAG):
            self.dg = None
        elif self.input.btnp(self.DRAG):
            self.dg = Dragging( (pyxel.mouse_x, pyxel.mouse_y), self.board.get_center_pos() )
        if pyxel.btn(self.DRAG) and self.dg is not None:
            nbp = self.dg.get_board_pos( (pyxel.mouse_x, pyxel.mouse_y) )
            self.__limited_move( (nbp[0], nbp[1]) )
        
        self.c_monitor.monitor_hover(self.piece_rotation)
        self.c_monitor.monitor_placement(self.game)
        # マウスホバーをもとにタイルを再生成
        cursored_tiles_data = self.commited_tiles_data.copy()
        self.c_monitor.write_hover_piece(cursored_tiles_data, 1)
        if not numpy.all(cursored_tiles_data == self.displaying_tiles_data):
            self.displaying_tiles_data = cursored_tiles_data
            self.board.set_tiles(self.__draw_tiles(self.displaying_tiles_data))

        # ピース設置を試行
        
        # ホイール検知・計算
        effected_scale = self.board.zoom(1 + self.input.get_wheel() * 0.1)
        bcc = self.board.get_center_pos()
        self.__limited_move( (
            bcc[0] + (effected_scale - 1) * (bcc[0] - pyxel.mouse_x),
            bcc[1] + (effected_scale - 1) * (bcc[1] - pyxel.mouse_y),
        ) )

        self.board.make_sizing_bi(self.c_monitor)
    
    def draw(self):
        self.board.draw()
        
    def __limited_move(self, to:Tuple[int, int]):
        """盤がビューの外に出ないようにしつつ盤を移動"""
        gap = self.DRAGGABLE_LIMIT_POCKET_PX
        self.board.to_center_pos(
            min(self.x + self.w + self.board.w / 2 - gap, max(self.x - self.board.w / 2 + gap, to[0])),
            min(self.y + self.h + self.board.w / 2 - gap, max(self.y - self.board.h / 2 + gap, to[1]))
        )
        
    def __draw_tiles(self, data: NDArray) -> pyxel.Image:
        """タイルマップをもとに画像を生成し、これを返す"""
        from pyxres import EMPTY_TILE_COOR, BLOCK_TILE_COOR, TILE_COLOR_PALLETS_NUMBER, DEFAULT_COLOR_S

        image = pyxel.Image(DraggableBoard.BOARD_SIZE_TILES * TILE_SIZE_PX, DraggableBoard.BOARD_SIZE_TILES * TILE_SIZE_PX)
        x = 0
        y = 0
        for column in data:
            y = 0
            for t in column:
                if t == 0: tile_coor = EMPTY_TILE_COOR
                else:
                    tile_coor = BLOCK_TILE_COOR
                    for i in range(TILE_COLOR_PALLETS_NUMBER): image.pal(i + DEFAULT_COLOR_S, i + BoardView.TILE_COLORS[t])
                image.blt(
                    x,
                    y,
                    pyxel.images[0],
                    tile_coor[0],
                    tile_coor[1],
                    TILE_SIZE_PX,
                    TILE_SIZE_PX
                )
                image.pal()

                y += TILE_SIZE_PX
            x += TILE_SIZE_PX
        return image

class Dragging:
    """ドラッグが開始してから離すまでが寿命のクラス"""
    def __init__(self, mouse_pos:Tuple[float, float], board_pos:Tuple[float, float]):
        self.mouse_pos = mouse_pos
        self.board_pos = board_pos
    
    def get_board_pos(self, curr_mouse_pos:Tuple[float, float]):
        return tuple(self.board_pos[i] + curr_mouse_pos[i] - self.mouse_pos[i] for i in range(2))

from pyxres import TILE_SIZE_PX

class DraggableBoard(CenteredArea):
    """移動可能な盤の座標系を表す"""
    from ..rule.rule import Rule
    BOARD_SIZE_TILES = Rule.BOARD_SIZE_TILES

    FRAME_THICKNESS = 10
    DEFAULT_BOARD_SIZE_PX = BOARD_SIZE_TILES * TILE_SIZE_PX + FRAME_THICKNESS * 2

    MIN_ZOOM = 0.5
    MAX_ZOOM = 25.0

    def __init__(self, cx:float, cy:float, drawer:LimitedDrawer, tiles: pyxel.Image):
        self.x = 0.0
        self.y = 0.0
        self.w = float(DraggableBoard.DEFAULT_BOARD_SIZE_PX)
        self.h = float(DraggableBoard.DEFAULT_BOARD_SIZE_PX)
        self.scale = 1.0
        self.drawer = drawer
        self.tiles = tiles
        self.to_center_pos(cx, cy)
    
    def ini_b_input(self, parent: BoardView, cursor: Cursor):
        F = DraggableBoard.FRAME_THICKNESS
        T = DraggableBoard.BOARD_SIZE_TILES * TILE_SIZE_PX
        return CursorMonitor(self.x + F, self.y + F, T, T, self.scale, parent, cursor)
    
    def set_tiles(self, value: pyxel.Image):
        self.tiles = value
    
    def zoom(self, scale:float):
        """現在の大きさに対しての拡大倍率を指定。さらに、中心位置を保持。"""
        prev_scale = self.scale
        self.scale = min(self.MAX_ZOOM, max(self.MIN_ZOOM, scale * self.scale))

        effected_scale = self.scale / prev_scale

        self.x -= self.w * (effected_scale - 1) / 2
        self.y -= self.h * (effected_scale - 1) / 2
        
        size = self.DEFAULT_BOARD_SIZE_PX * self.scale
        self.w = size
        self.h = size

        return effected_scale
    
    def make_sizing_bi(self, bi: 'CursorMonitor'):
        """BoardInputの形を、適切な形に調整。"""
        F = DraggableBoard.FRAME_THICKNESS
        bi.x = self.x + F * self.scale
        bi.y = self.y + F * self.scale

        T = DraggableBoard.BOARD_SIZE_TILES * TILE_SIZE_PX
        bi.w = T * self.scale
        bi.h = T * self.scale

        bi.scale = self.scale

    def draw(self):
        # フレーム
        self.drawer.rect(self.x + 2 * self.scale, self.y + 2 * self.scale, self.w, self.h, 3)
        self.drawer.rect(self.x - 2 * self.scale, self.y - 2 * self.scale, self.w, self.h, 2)
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)

        # タイル
        self.drawer.blt(
            self.x + self.FRAME_THICKNESS * self.scale + (self.scale - 1) * self.tiles.width / 2,
            self.y + self.FRAME_THICKNESS * self.scale + (self.scale - 1) * self.tiles.height / 2,
            self.tiles,
            0,
            0,
            self.tiles.width,
            self.tiles.height,
            scale=self.scale
        )

class CursorMonitor(LimitableArea):
    """盤のマウス入力についての座標系であり、DraggableBoardに追従する。"""
    def __init__(self, x, y, w, h, scale: float, limitation_area: BoardView, cursor: Cursor):
        super().__init__(x, y, w, h)
        self.set_limiteds(limitation_area.surface)
        self.scale = scale
        self.prev_hovered = False
        self.cursor = cursor
        self.__count_hover_piece(Rotation.DEFAULT)
    
    def monitor_hover(self, rotation: Rotation):
        iir = self.input.is_in_range()
        
        if iir:
            self.__count_hover_piece(rotation)

        if (
            (self.prev_hovered and not iir) or
            (not self.prev_hovered and iir)
        ):
            self.prev_hovered = iir
            if self.cursor.held is not None: self.cursor.held.set_visibility(not iir)

    def monitor_placement(self, game: Rule):
        if (
            btnp(Bind.PLACE_PIECE) and 
            self.input.is_in_range() and 
            self.cursor.held is not None and 
            self.hover_piece_start_coord is not None
        ):
            self.cursor.held.clear()
                

    def __limit_in_board(self, x, y):
        SIZE = DraggableBoard.BOARD_SIZE_TILES
        return (
            max(0, min(SIZE - 1, x)),
            max(0, min(SIZE - 1, y)),
        )

    def __count_hover_piece(self, rotation: Rotation):
        if self.cursor.held is None:
            self.hover_piece_shape = None
            self.hover_piece_start_coord = None
        else:
            SIZE = DraggableBoard.BOARD_SIZE_TILES
            cursor_coord = self.__limit_in_board(
                int( (pyxel.mouse_x - self.x) / (self.w / (SIZE)) ),
                int( (pyxel.mouse_y - self.y) / (self.h / (SIZE)) )
            )

            shape = self.cursor.held.piece.to_ndarray()
            
            r = rotation
            rotation_times = 0
            if r == Rotation.RIGHT_90: rotation_times = 1
            elif r == Rotation.RIGHT_180: rotation_times = 2
            elif r == Rotation.RIGHT_270: rotation_times = 3

            shape = numpy.fliplr(shape)
            shape = numpy.rot90(shape, (rotation_times + 1) % 4)

            diff = None
            for (row, col), value in numpy.ndenumerate(shape):
                if value == Piece.CENTER: diff = (row, col)
            if diff is None: assert False, "'.rule.rule.Piece.SHAPES'のいずれかのPiece形状の定義は、Piece.CENTER（0の値）の値が無い。"

            start_coord = (
                cursor_coord[0] - diff[0],
                cursor_coord[1] - diff[1]
            )

            self.hover_piece_shape = shape
            self.hover_piece_start_coord = start_coord

    def write_hover_piece(self, data: NDArray, tile_value: int) -> None:
        """２次元地図形式のタイルデータに、カーソルホバーによるピースを書き入れる"""
        if self.input.is_in_range() and self.hover_piece_shape is not None and self.hover_piece_start_coord is not None:
            for (row, col), value in numpy.ndenumerate(self.hover_piece_shape):
                if value in (Piece.TILED, Piece.CENTER):
                    target = self.__limit_in_board(
                        self.hover_piece_start_coord[0] + row,
                        self.hover_piece_start_coord[1] + col
                    )
                    data[target[0]][target[1]] = tile_value
