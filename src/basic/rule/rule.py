from typing import Tuple, Dict
import numpy

class Piece:
    SHAPES = (
        (
            (1, ),
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

    def __init__(self, shape: numpy.ndarray):
        self.shape: numpy.ndarray = shape
    
    @staticmethod
    def get_piece_set():
        return tuple(Piece( numpy.array(s) ) for s in Piece.SHAPES)

    def get_width(self):
        return self.shape.shape[0]
    
    def get_height(self):
        return self.shape.shape[1]

class Rule:
    """ゲームルールに基づきデータをアップデートさせ、さらに現在のデータを提供する"""
    PLAYER1 = 0
    PLAYER2 = 1

    def __init__(self):
        self.data = GameData(Rule.PLAYER1, {
            Rule.PLAYER1: Piece.get_piece_set(),
            Rule.PLAYER2: Piece.get_piece_set()
        } )
    
    def switch_turn(self):
        self.data.turn = (self.data.turn + 1) % len(self.data.pieces_by_player)
    
    def get_turn(self):
        return self.data.turn
    
    def get_pieces(self, which_player: int):
        return self.data.pieces_by_player[which_player]

class GameData:
    """ゲーム進行状況を維持する最低限のデータ"""
    def __init__(self, turn: int, pieces_by_player: Dict[int, Tuple[Piece]]):
        self.pieces_by_player = pieces_by_player
        self.turn = turn


if __name__ == '__main__':
    game = Rule()
    print(game.data.pieces_by_player[Rule.PLAYER1][3].shape)
    for i in range(5):
        game.switch_turn()
        print(game.get_turn())
    for p in game.data.pieces_by_player[Rule.PLAYER1]:
        print(p.shape)
        print(p.get_width())
        print(p.get_height())
