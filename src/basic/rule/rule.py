from typing import *
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
    CENTER = 2

    from .piece_shape import SHAPES

    def __init__(self, shape: numpy.ndarray):
        self.shape = shape
    
    @staticmethod
    def get_piece_set():
        return tuple(Piece( numpy.array(s) ) for s in Piece.SHAPES)

    def copy_shape(self):
        return self.shape.copy()

    def get_width_tiles(self):
        return self.shape.shape[1]
    
    def get_height_tiles(self):
        return self.shape.shape[0]

    def copy_rotated_right90(self, times: int):
        s = numpy.rot90(self.shape.copy(), times)
        return Piece(s)

    def copy_rotated(self, rotation: Rotation):
        rotation_times = 0
        if rotation == Rotation.RIGHT_90: rotation_times = 1
        elif rotation == Rotation.RIGHT_180: rotation_times = 2
        elif rotation == Rotation.RIGHT_270: rotation_times = 3
        
        return self.copy_rotated_right90(rotation_times)

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

class GameData:
    """ゲーム進行状況を維持する最低限のデータ"""
    def __init__(self, turn: int, pieces_by_player: List[Tuple[Piece]], board_size: int):
        self.pieces_by_player = pieces_by_player
        self.turn = turn
        self.board_size = board_size
    
    def limit_in_board(self, coordinate: Tuple[int, int]):
        s = self.board_size - 1
        return (
            max(0, min(s, coordinate[0])),
            max(0, min(s, coordinate[1]))
        )

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
