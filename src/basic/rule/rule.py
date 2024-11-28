from typing import Tuple, Dict
import enum
import numpy

class Rotation(enum.Enum):
    DEFAULT = 0
    RIGHT_90 = 1
    RIGHT_180 = 2
    RIGHT_270 = 3

    @staticmethod
    def cw(rotation: "Rotation") -> "Rotation":
        return Rotation((rotation.value + 1) % 4)

    @staticmethod
    def counter_cw(rotation: "Rotation") -> "Rotation":
        return Rotation((rotation.value + 3) % 4)


class Piece:
    EMPTY = 0
    TILED = 1

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
        (
            (1, ),
            (1, ),
            (1, ),
            (1, ),
        ),
        (
            (0, 1),
            (0, 1),
            (1, 1),
        )
    )

    def __init__(self, shape: numpy.ndarray):
        self.shape = shape
    
    @staticmethod
    def get_piece_set():
        return tuple(Piece( numpy.array(s) ) for s in Piece.SHAPES)

    def get_width_tiles(self):
        return self.shape.shape[1]
    
    def get_height_tiles(self):
        return self.shape.shape[0]

    def copy_rotated_right90(self, times: int):
        s = numpy.rot90(self.shape, times)
        return Piece(s)

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
        print(p.get_width_tiles())
        print(p.get_height_tiles())
