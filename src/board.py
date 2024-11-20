from view import ViewArea
from limitter import LimitedDrawer, LimitedMouseInput
from typing import Tuple, List
import pyxel

class BoardView(ViewArea):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.drawer = LimitedDrawer(self)
        self.input = LimitedMouseInput(self)
        self.board = DraggableBoard(self.x + self.w // 2, self.y + self.h // 2, self.drawer)
    
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
class DraggableBoard:
    TILES_ZERO_ADDITION = 10
    TILE_SIZE_PX = 8

    BOARD_SIZE_TILES = 20

    def __init__(self, cx:float, cy:float, drawer:LimitedDrawer):
        self.x = 0.0
        self.y = 0.0
        self.w = self.BOARD_SIZE_TILES * self.TILE_SIZE_PX + self.TILES_ZERO_ADDITION * 2
        self.h = self.BOARD_SIZE_TILES * self.TILE_SIZE_PX + self.TILES_ZERO_ADDITION * 2
        self.drawer = drawer
        self.tiles = self.__draw_tiles( [[1 for _ in range(self.BOARD_SIZE_TILES)] for _ in range(self.BOARD_SIZE_TILES)] )
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

        self.drawer.lblt(
            self.x + self.TILES_ZERO_ADDITION,
            self.y + self.TILES_ZERO_ADDITION,
            self.tiles,
            0,
            0,
            self.BOARD_SIZE_TILES * self.TILE_SIZE_PX,
            self.BOARD_SIZE_TILES * self.TILE_SIZE_PX
        )
    
    def __draw_tiles(self, data:List[List[int]]) -> pyxel.Image:
        EMPTY_TILE_COOR = (0, 0)
        BLOCK_TILE_COOR = (8, 0)
        TILE_COLOR_PALLET_NUMBER = 4
        DEFAULT_COLOR_S = 1
        RED_COLOR_S = 4

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
