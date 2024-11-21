from limitter import LimitableView, LimitedDrawer
from typing import List, Tuple
import pyxel

class BoardView(LimitableView):
    """DraggableBoardの表示限界を表す"""
    DRAGGABLE_LIMIT_POCKET_PX = 50
    DRAG = pyxel.MOUSE_BUTTON_RIGHT

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.board = DraggableBoard(self.x + self.w // 2, self.y + self.h // 2, self.drawer)
        self.dg: Dragging | None = None
    
    def update(self):
        # ドラッグ検知・計算
        if pyxel.btnr(self.DRAG):
            self.dg = None
        elif self.input.btnp(self.DRAG):
            self.dg = Dragging( (pyxel.mouse_x, pyxel.mouse_y), self.board.get_center_coordinates() )
        if pyxel.btn(self.DRAG) and self.dg is not None:
            nbp = self.dg.get_board_pos( (pyxel.mouse_x, pyxel.mouse_y) )
            self.__limited_move( (nbp[0], nbp[1]) )
        
        # ホイール検知・計算
        p = self
        if (
            p.x <= pyxel.mouse_x and
            p.y <= pyxel.mouse_y and
            pyxel.mouse_x <= p.x + p.w and
            pyxel.mouse_y <= p.y + p.h
        ):
            effected_scale = self.board.zoom(1 + pyxel.mouse_wheel * 0.1)
            bcc = self.board.get_center_coordinates()
            self.__limited_move( (
                bcc[0] + (effected_scale - 1) * (bcc[0] - pyxel.mouse_x),
                bcc[1] + (effected_scale - 1) * (bcc[1] - pyxel.mouse_y),
            ) )

    def __limited_move(self, to:Tuple[int, int]):
        """盤がビューの外に出ないようにしつつ盤を移動"""
        gap = self.DRAGGABLE_LIMIT_POCKET_PX
        self.board.to_center_coordinates(
            min(self.x + self.w + self.board.w / 2 - gap, max(self.x - self.board.w / 2 + gap, to[0])),
            min(self.y + self.h + self.board.w / 2 - gap, max(self.y - self.board.h / 2 + gap, to[1]))
        )
    
    def draw(self):
        self.board.draw()

class Dragging:
    """ドラッグが開始してから離すまでが寿命のクラス"""
    def __init__(self, mouse_pos:Tuple[float, float], board_pos:Tuple[float, float]):
        self.mouse_pos = mouse_pos
        self.board_pos = board_pos
    
    def get_board_pos(self, curr_mouse_pos:Tuple[float, float]) -> Tuple[float, float]:
        return tuple(self.board_pos[i] + curr_mouse_pos[i] - self.mouse_pos[i] for i in range(2))

class DraggableBoard:
    """移動可能な盤の座標系を表す"""
    FRAME_THICKNESS = 10
    TILE_SIZE_PX = 8

    BOARD_SIZE_TILES = 20

    DEFAULT_BOARD_SIZE_PX = BOARD_SIZE_TILES * TILE_SIZE_PX + FRAME_THICKNESS * 2
    MIN_ZOOM = 1.0
    MAX_ZOOM = 25.0

    def __init__(self, cx:float, cy:float, drawer:LimitedDrawer):
        self.x = 0.0
        self.y = 0.0
        self.w = float(self.DEFAULT_BOARD_SIZE_PX)
        self.h = float(self.DEFAULT_BOARD_SIZE_PX)
        self.scale = 1.0
        self.drawer = drawer
        self.tiles = self.__draw_tiles( [[0 for _ in range(self.BOARD_SIZE_TILES)] for _ in range(self.BOARD_SIZE_TILES)] )
        self.to_center_coordinates(cx, cy)
    
    def to_center_coordinates(self, cx:float, cy:float):
        self.x = cx - self.w / 2
        self.y = cy - self.h / 2
    
    def get_center_coordinates(self):
        return (self.x + self.w / 2, self.y + self.h / 2)
    
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

    def draw(self):
        # フレーム
        self.drawer.rect(self.x + 2 * self.scale, self.y + 2 * self.scale, self.w, self.h, 3)
        self.drawer.rect(self.x - 2 * self.scale, self.y - 2 * self.scale, self.w, self.h, 2)
        self.drawer.rect(self.x, self.y, self.w, self.h, 1)

        # タイル
        self.drawer.lblt(
            self.x + self.FRAME_THICKNESS * self.scale + (self.scale - 1) * self.tiles.width / 2,
            self.y + self.FRAME_THICKNESS * self.scale + (self.scale - 1) * self.tiles.height / 2,
            self.tiles,
            0,
            0,
            self.BOARD_SIZE_TILES * self.TILE_SIZE_PX,
            self.BOARD_SIZE_TILES * self.TILE_SIZE_PX,
            scale=self.scale
        )
    
    def __draw_tiles(self, data:List[List[int]]) -> pyxel.Image:
        """タイルマップをもとに画像を生成し、これを返す"""
        EMPTY_TILE_COOR = (0, 0)
        BLOCK_TILE_COOR = (8, 0)
        TILE_COLOR_PALLET_NUMBER = 4
        DEFAULT_COLOR_S = 1
        RED_COLOR_S = 4
        BLUE_COLOR_S = 7

        image = pyxel.Image(self.BOARD_SIZE_TILES * self.TILE_SIZE_PX, self.BOARD_SIZE_TILES * self.TILE_SIZE_PX)
        x = 0
        y = 0
        for column in data:
            y = 0
            for t in column:
                if t == 0: tile_coor = EMPTY_TILE_COOR
                else:
                    tile_coor = BLOCK_TILE_COOR
                    if t == 1:
                        for i in range(TILE_COLOR_PALLET_NUMBER): image.pal(i + DEFAULT_COLOR_S, i + RED_COLOR_S)
                    elif t == 2:
                        for i in range(TILE_COLOR_PALLET_NUMBER): image.pal(i + DEFAULT_COLOR_S, i + BLUE_COLOR_S)
                image.blt(
                    x,
                    y,
                    pyxel.images[0],
                    tile_coor[0],
                    tile_coor[1],
                    self.TILE_SIZE_PX,
                    self.TILE_SIZE_PX
                )
                image.pal()

                y += self.TILE_SIZE_PX
            x += self.TILE_SIZE_PX
        return image
