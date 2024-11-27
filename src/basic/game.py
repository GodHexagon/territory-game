from .rule.rule import Rule, Rotation
from .view.view import Area, ParenthoodView
from .view import *
from .key_bind import *
from pyxres import BLUE_COLOR_S
from typing import Dict

class GameView(Area, ParenthoodView):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        
        self.game = Rule()
        self.rotation = Rotation.DEFAULT
        
        new = Cursor()

        board_view_end_y = int(h * 0.6)
        self.childs: Dict[View] = {
            "b": BoardView(0, 0, w, board_view_end_y, new, BLUE_COLOR_S),
            "p": PickerView(
                0, 
                board_view_end_y + 1, 
                w, 
                h - board_view_end_y - 1, 
                self.game.get_pieces(Rule.PLAYER1),
                BLUE_COLOR_S,
                new
            ),
            'c': new
        }
    
    def update(self):
        if btnp(Bind.ROTATE_LEFT):
            self.rotation = Rotation.counter_cw(self.rotation)
        if btnp(Bind.ROTATE_RIGHT):
            self.rotation = Rotation.cw(self.rotation)
        picker: PickerView = self.childs['p']
        picker.set_piece_rotation(self.rotation)

        return super().update()
    
    def draw(self):
        return super().draw()
