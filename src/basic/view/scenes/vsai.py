from ...rule.rule import RuleVSAI, Rotation
from ...rule.data import GameData
from ..view import Area, View
from ..areas import *
from ...key_bind import *

from pyxres import BLUE_COLOR_S, RED_COLOR_S
from typing import Dict

import pyxel
from pyxel import Image

class VSAIGameView(Area, View):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        
        self.game = RuleVSAI()
        self.game.set_on_change_pieces(self.on_change_pieces)
        self.game.set_on_end(self.on_end)
        self.game.set_on_give_up(self.on_give_up)

        self.rotation = Rotation.DEFAULT
        
        self.cursor = Cursor()

        board_view_end_y = int(y + h * 0.6)
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
        self.notice.put('GAME START!', frame_to_hide=60)

        self.result = VSAIResultView(x + (w - 300) / 2, board_view_end_y - 100, 300, 150)

        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)
    
    def on_change_pieces(self, player: int, data: GameData):
        if RuleVSAI.PLAYER == player:
            self.picker.reset_pieces(
                p.shape for p in data.pieces_by_player[player] if not p.placed()
            )
            held = self.cursor.held
            if held is not None:
                held.clear()
        self.board.rewrite_board(tuple(data.pieces_by_player), (BLUE_COLOR_S, RED_COLOR_S))

    def on_end(self):
        scores = self.game.get_scores()
        self.result.show( (scores[0], scores[1]), (BLUE_COLOR_S, RED_COLOR_S), scores[0] > scores[1] )
    
    def on_give_up(self, player: int):
        if player == RuleVSAI.AI:
            self.notice.put('THE ENEMY GAVE UP!')
    
    def update(self):
        if btnp(Bind.ROTATE_LEFT):
            self.rotation = Rotation.counter_cw(self.rotation)
        if btnp(Bind.ROTATE_RIGHT):
            self.rotation = Rotation.cw(self.rotation)
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        if btnp(Bind.GIVE_UP):
            self.game.give_up()

        self.picker.update()
        self.board.update()
        self.cursor.update()
        self.notice.update()
        self.result.update()
    
    def draw(self):
        self.board.draw()
        self.picker.draw()
        self.cursor.draw()
        self.notice.draw()
        self.result.draw()

from pyxres import CHAR_HEIGHT_PX, CHAR_WIDTH_PX

class VSAIResultView(Area, View):
    BORDER_THICKNESS_PX = 5

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.title = self.__get_typo_image('RESULT', 0)
        self.scores: Tuple[Image, Image] | None = None
    
    def show(self, scores: Tuple[int, int], colors: Tuple[int, int], win: bool):
        self.scores = (self.__get_typo_image(f"YOU: {scores[0]}", colors[0]), self.__get_typo_image(f"ENEMY: {scores[1]}", colors[1]))

        from pyxres import COLOR_SUCCESSFULL, COLOR_FAILURE
        if win: self.title = self.__get_typo_image("VICTORY!", COLOR_SUCCESSFULL)
        else: self.title = self.__get_typo_image("DEFEAT", COLOR_FAILURE)
    
    def __get_typo_image(self, value: str, color: int):
        self.t_w = max(0, len(value) * CHAR_WIDTH_PX - 1)
        img = Image(self.t_w, CHAR_HEIGHT_PX)
        img.cls(1)
        img.text(0, 0, value, color, None)
        return img
    
    def update(self):
        pass

    def draw(self):
        if self.scores is not None:
            border = VSAIResultView.BORDER_THICKNESS_PX
            pyxel.rect(self.x, self.y, self.w, self.h, 16)
            pyxel.rect(self.x + border, self.y + border, self.w - border * 2, self.h - border * 2, 1)
            pyxel.blt(
                self.x + (self.w - self.t_w) / 2,
                self.y + 30,
                self.title,
                0, 0, self.title.width, self.title.height,
                colkey=1,
                scale=4
            )
            p, e = self.scores
            pyxel.blt(
                self.x + 50,
                self.y + 60,
                p,
                0, 0, p.width, p.height,
                colkey=1,
                scale=3
            )
            pyxel.blt(
                self.x + 50,
                self.y + 90,
                e,
                0, 0, e.width, e.height,
                colkey=1,
                scale=3
            )
