from ...base.view import Area, View
from ...areas import *
from ....rule.rule import Rotation, TilesMap

from ....key_bind import *

from abc import ABC, abstractmethod
from typing import *

class GameScene(Area, View, ABC):
    def init_view(self, primary_color_s: int, picker_shapes: Tuple[TilesMap]):
        x, y, w, h = self.x, self.y, self.w, self.h
        
        self.rotation = Rotation.DEFAULT

        self.cursor = Cursor()

        board_view_end_y = int(y + h * 0.6)
        self.board = BoardView(
            x, 
            y, 
            w, 
            board_view_end_y, 
            self.cursor, 
            primary_color_s,
            self.hdl_place_piece
        )
        self.picker = PickerView(
            0, 
            board_view_end_y + 1, 
            w, 
            h - board_view_end_y - 1, 
            picker_shapes,
            primary_color_s,
            self.cursor
        )
        
        self.result = ResultWindow(x + (w - 300) / 2, board_view_end_y - 100, 300, 200)
        
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        self.notice = FrontNoticeView(x + w / 2 - 150, y + h * 0.3, 300, 50)
        self.notice.put('GAME START!', frame_to_hide=60)
    
    @abstractmethod
    def hdl_place_piece(self, shape: TilesMap, rotation: Rotation, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def hdl_give_up(self) -> bool:
        pass
    
    def update(self):
        if btnp(Bind.ROTATE_LEFT):
            self.rotation = Rotation.counter_cw(self.rotation)
        if btnp(Bind.ROTATE_RIGHT):
            self.rotation = Rotation.cw(self.rotation)
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        if btnp(Bind.GIVE_UP):
            self.hdl_give_up()
        
        self.picker.update()
        self.board.update()
        self.notice.update()
        self.result.update()
        self.cursor.update()
        
    def draw(self):
        self.board.draw()
        self.picker.draw()
        self.notice.draw()
        self.result.draw()
        self.cursor.draw()
