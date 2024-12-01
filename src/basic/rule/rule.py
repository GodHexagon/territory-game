from typing import *
import enum

import numpy

from .data import Rotation, GameData, Piece

class Rule:
    """ゲームルールに基づきデータをアップデートさせ、さらに現在のデータを提供する"""
    BOARD_SIZE_TILES = 20

    def create_game_data(self, players_number: int):
        self.data = GameData(
            0,
            [Piece.get_piece_set() for _ in range(players_number)],
            Rule.BOARD_SIZE_TILES
        )
        #self.next_pm = PlacableModel.get_next_pm(self.data)
    
    def place(self, piece: Piece, rotation: Rotation, x, y) -> bool:
        pbp = self.data.pieces_by_player[self.data.turn]
        if not any(piece is p for p in pbp): return False

        rotated = piece.copy_rotated_right90(rotation)
        

        self.data.turn = (self.data.turn + 1) % len(self.data.pieces_by_player)
        return True
    
    def get_turn(self):
        return self.data.turn
    
    def get_pieces(self, which_player: int):
        return self.data.pieces_by_player[which_player]

class PlacableModel:
    def __init__(self, col: Tuple[Tuple[bool]], sur: Tuple[Tuple[bool]], cor: Tuple[Tuple[bool]]):
        self.col = col
        self.sur = sur
        self.cor = cor
    
    @staticmethod
    def get_next_pm(data: 'GameData'):
        col = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        sur = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        cor = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        
        for pieces in data.pieces_by_player:
            pass

        return PlacableModel(
            
        )

class RuleVSAI(Rule):
    PLAYER = 0
    AI = 1
    def __init__(self):
        self.create_game_data(2)


if __name__ == '__main__':
    game = Rule()
    print(game.data.pieces_by_player[Rule.PLAYER1][3].shape)
    for i in range(5):
        game.place()
        print(game.get_turn())
    for p in game.data.pieces_by_player[Rule.PLAYER1]:
        print(p.shape)
        print(p.get_width_tiles())
        print(p.get_height_tiles())
