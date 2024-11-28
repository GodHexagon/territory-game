from .limitter import LimitableArea, LimitedDrawer
from .view import View, CenteredArea
from .cursor import Cursor
from pyxres import DEFAULT_COLOR_S, RED_COLOR_S, BLUE_COLOR_S

from typing import List, Tuple

import pyxel

class BoardView(View, LimitableArea):
    """DraggableBoardの表示限界。"""
    DRAGGABLE_LIMIT_POCKET_PX = 50
    DRAG = pyxel.MOUSE_BUTTON_RIGHT
    
    TILE_COLORS = (DEFAULT_COLOR_S, BLUE_COLOR_S, RED_COLOR_S)

    def __init__(self, x, y, w, h, cursor: Cursor, colors_s: int):
        super().__init__(x, y, w, h)

        self.tiles_data = [[0 for _ in range(DraggableBoard.BOARD_SIZE_TILES)] for _ in range(DraggableBoard.BOARD_SIZE_TILES)]

        self.board = DraggableBoard(
            self.x + self.w // 2, 
            self.y + self.h // 2, 
            self.drawer, 
            self.__draw_tiles(self.tiles_data)
        )

        self.b_input = self.board.ini_b_input()
        self.cursor = cursor
        self.color_s = colors_s
        self.dg: Dragging | None = None
    
    def update(self):
        # ドラッグ検知・計算
        if pyxel.btnr(self.DRAG):
            self.dg = None
        elif self.input.btnp(self.DRAG):
            self.dg = Dragging( (pyxel.mouse_x, pyxel.mouse_y), self.board.get_center_pos() )
        if pyxel.btn(self.DRAG) and self.dg is not None:
            nbp = self.dg.get_board_pos( (pyxel.mouse_x, pyxel.mouse_y) )
            self.__limited_move( (nbp[0], nbp[1]) )
        
        # マウスホバーをもとにタイルを再生成
        new_tiles_data = self.b_input.get_tiles_data(self.cursor, BoardView.TILE_COLORS[0])
        if new_tiles_data != self.tiles_data:
            self.tiles_data = new_tiles_data
            self.board.set_tiles(self.__draw_tiles(self.tiles_data))
        
        # ホイール検知・計算
        effected_scale = self.board.zoom(1 + self.input.get_wheel() * 0.1)
        bcc = self.board.get_center_pos()
        self.__limited_move( (
            bcc[0] + (effected_scale - 1) * (bcc[0] - pyxel.mouse_x),
            bcc[1] + (effected_scale - 1) * (bcc[1] - pyxel.mouse_y),
        ) )

        self.board.make_sizing_bi(self.b_input)
        self.b_input.update(self.cursor)
    
    def draw(self):
        self.board.draw()
        
    def __limited_move(self, to:Tuple[int, int]):
        """盤がビューの外に出ないようにしつつ盤を移動"""
        gap = self.DRAGGABLE_LIMIT_POCKET_PX
        self.board.to_center_pos(
            min(self.x + self.w + self.board.w / 2 - gap, max(self.x - self.board.w / 2 + gap, to[0])),
            min(self.y + self.h + self.board.w / 2 - gap, max(self.y - self.board.h / 2 + gap, to[1]))
        )
        
    def __draw_tiles(self, data:List[List[int]]) -> pyxel.Image:
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
    FRAME_THICKNESS = 10

    BOARD_SIZE_TILES = 20

    DEFAULT_BOARD_SIZE_PX = BOARD_SIZE_TILES * TILE_SIZE_PX + FRAME_THICKNESS * 2
    MIN_ZOOM = 1.0
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
    
    def ini_b_input(self):
        F = DraggableBoard.FRAME_THICKNESS
        T = DraggableBoard.BOARD_SIZE_TILES * TILE_SIZE_PX
        return BoardInput(self.x + F, self.y + F, T, T, self.scale)
    
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
    
    def make_sizing_bi(self, bi: 'BoardInput'):
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

class BoardInput(LimitableArea):
    def __init__(self, x, y, w, h, scale: float):
        super().__init__(x, y, w, h)
        self.scale = scale
        self.prev_hovered = False
    
    def update(self, cursor: Cursor):
        iir = self.input.is_in_range()
        if (
            (self.prev_hovered and not iir) or
            (not self.prev_hovered and iir)
        ):
            self.prev_hovered = iir
            if cursor.held is not None: cursor.held.set_visibility(not iir)

    def get_tiles_data(self, cursor: Cursor, held_piece_tile: int) -> List[List[int]]:
        MAX_INDEX = DraggableBoard.BOARD_SIZE_TILES - 1
        cursor_coord = (
            max(0, min( MAX_INDEX, int((pyxel.mouse_x - self.x) / (self.w / (MAX_INDEX + 1))) )),
            max(0, min( MAX_INDEX, int((pyxel.mouse_y - self.y) / (self.h / (MAX_INDEX + 1))) ))
        )

        data = [[0 for _ in range(DraggableBoard.BOARD_SIZE_TILES)] for _ in range(DraggableBoard.BOARD_SIZE_TILES)]
        if self.input.is_in_range(): data[cursor_coord[0]][cursor_coord[1]] = 1

        return data
