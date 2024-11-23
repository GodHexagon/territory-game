from .view import Area, View, ParenthoodView
from .board import BoardView
from .picker import PickerView
from typing import Dict

class GameView(Area, ParenthoodView):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        
        board_view_end_y = int(h * 0.6)
        self.childs: Dict[View] = {
            "b": BoardView(0, 0, w, board_view_end_y),
            "p": PickerView(0, board_view_end_y + 1, w, h - board_view_end_y - 1)
        }
    
    def update(self):
        return super().update()
    
    def draw(self):
        return super().draw()
