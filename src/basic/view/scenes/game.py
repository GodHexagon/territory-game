from ...rule.rule import RuleVSAI, Rotation
from ...rule.data import GameData
from ..view import Area, ParenthoodView, View
from ..areas import *
from ...key_bind import *

from pyxres import BLUE_COLOR_S, RED_COLOR_S
from typing import Dict

class GameView(Area, View):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        
        self.game = RuleVSAI()
        self.game.set_on_change_pieces(self.on_change_pieces)
        self.game.set_on_end(self.on_end)
        self.game.set_on_give_up(self.on_give_up)

        self.rotation = Rotation.DEFAULT
        
        self.cursor = Cursor()

        board_view_end_y = int(h * 0.6)
        self.board = BoardView(0, 0, w, board_view_end_y, self.cursor, BLUE_COLOR_S, self.game)
        self.picker = PickerView(
            0, 
            board_view_end_y + 1, 
            w, 
            h - board_view_end_y - 1, 
            self.game.get_pieces_shape(RuleVSAI.PLAYER),
            BLUE_COLOR_S,
            self.cursor
        )

        self.notice = FrontNoticeView(x + w / 2 - 150, y + h * 0.3, 300, 50)
        self.notice.put('Game Start!')

        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)
    
    def on_change_pieces(self, player: int, data: GameData):
        if RuleVSAI.PLAYER == player:
            self.picker.reset_pieces(
                p.shape for p in data.pieces_by_player[player] if not p.placed()
            )
        self.board.rewrite_board(tuple(data.pieces_by_player), (BLUE_COLOR_S, RED_COLOR_S))

    def on_end(self):
        self.notice.put('Game Finish!')
    
    def on_give_up(self, player: int):
        if player == RuleVSAI.AI:
            self.notice.put('AI exited the game!')
    
    def update(self):
        if btnp(Bind.ROTATE_LEFT):
            self.rotation = Rotation.counter_cw(self.rotation)
        if btnp(Bind.ROTATE_RIGHT):
            self.rotation = Rotation.cw(self.rotation)
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        self.picker.update()
        self.board.update()
        self.cursor.update()
        self.notice.update()
    
    def draw(self):
        self.board.draw()
        self.picker.draw()
        self.cursor.draw()
        self.notice.draw()