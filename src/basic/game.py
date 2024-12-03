from .rule.rule import RuleVSAI, Rotation
from .rule.data import GameData
from .view.view import Area, ParenthoodView
from .view import *
from .key_bind import *
from pyxres import BLUE_COLOR_S
from typing import Dict

class GameView(Area, ParenthoodView):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        
        self.game = RuleVSAI(self.on_change_pieces)
        self.rotation = Rotation.DEFAULT
        
        new = Cursor()

        board_view_end_y = int(h * 0.6)
        self.childs: Dict[View] = {
            "b": BoardView(0, 0, w, board_view_end_y, new, BLUE_COLOR_S, self.game),
            "p": PickerView(
                0, 
                board_view_end_y + 1, 
                w, 
                h - board_view_end_y - 1, 
                self.game.get_pieces_shape(RuleVSAI.PLAYER),
                BLUE_COLOR_S,
                new
            ),
            'c': new
        }
        
        picker: PickerView = self.childs['p']
        picker.set_piece_rotation(self.rotation)
        board: BoardView = self.childs['b']
        board.set_piece_rotation(self.rotation)
        cursor: Cursor = self.childs['c']
        cursor.set_rotation(self.rotation)
    
    def on_change_pieces(self, player: int, data: GameData):
        assert False, 'ピースが置かれた！'
    
    def update(self):
        if btnp(Bind.ROTATE_LEFT):
            self.rotation = Rotation.counter_cw(self.rotation)
        if btnp(Bind.ROTATE_RIGHT):
            self.rotation = Rotation.cw(self.rotation)
        picker: PickerView = self.childs['p']
        picker.set_piece_rotation(self.rotation)
        board: BoardView = self.childs['b']
        board.set_piece_rotation(self.rotation)
        cursor: Cursor = self.childs['c']
        cursor.set_rotation(self.rotation)

        return super().update()
    
    def draw(self):
        return super().draw()
