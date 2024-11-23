from typing import Tuple, Dict
import numpy

class Piece:
    SHAPES = (
        (
            (0, 1),
        ),
        (
            (1, ),
            (1, ),
        ),
        (
            (1, ),
            (1, ),
            (1, ),
        ),
        (
            (1, 0),
            (1, 1),
        ),
    )

    def __init__(self, shape):
        self.shape = shape
    
    @staticmethod
    def get_piece_set():
        return tuple(Piece( numpy.array(s) ) for s in Piece.SHAPES)

class Rule:
    """ゲームルールに基づきデータをアップデートさせ、さらに現在のデータを提供する"""

    def __init__(self):
        self.data = GameData( {
            GameData.PLAYER1: Piece.get_piece_set(),
            GameData.PLAYER2: Piece.get_piece_set()
        } )
    
    def switch_turn(self):
        self.data.turn = (self.data.turn + 1) % len(self.data.pieces_by_player)
    
    def get_turn(self):
        return self.data.turn
    
    def get_pieces(self, which_player: int):
        return self.data.pieces_by_player[which_player]

class GameData:
    """ゲーム進行状況を維持する最低限のデータ"""
    PLAYER1 = 0
    PLAYER2 = 1
    
    def __init__(self, pieces_by_player: Dict[int, Tuple[Piece]]):
        self.pieces_by_player = pieces_by_player
        self.turn = GameData.PLAYER1


if __name__ == '__main__':
    game = Rule()
    print(game.data.pieces_by_player[GameData.PLAYER1][3].shape)
    for i in range(5):
        game.switch_turn()
        print(game.get_turn())
