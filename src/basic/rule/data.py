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

class GameData:
    """ゲーム進行状況を維持する最低限のデータ"""
    def __init__(self, turn: int, pieces_by_player: List[Tuple['Piece']], board_size: int):
        self.pieces_by_player = pieces_by_player
        self.turn = turn
        self.board_size = board_size
    
    def limit_in_board(self, coordinate: Tuple[int, int]):
        s = self.board_size - 1
        return (
            max(0, min(s, coordinate[0])),
            max(0, min(s, coordinate[1]))
        )

class Piece:
    EMPTY = 0
    TILED = 1
    CENTER = 2

    Unplaced: TypeAlias = None

    from .pieces_shape import SHAPES

    def __init__(self, shape: numpy.ndarray):
        self.shape = shape
        self.position: Tuple[int, int] | Piece.Unplaced = Piece.Unplaced
    
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
