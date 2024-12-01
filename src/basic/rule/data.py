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

class TilesMap:
    def __init__(self, input_array: numpy.ndarray):
        # 入力が ndarray でない場合、自動変換
        if not isinstance(input_array, numpy.ndarray):
            input_array = numpy.array(input_array)
        
        if input_array.ndim != 2:
            raise ValueError("TileMap only supports 2D arrays.")
        
        self._map = input_array
        self.height, self.width = input_array.shape

    def copy(self):
        return TilesMap(self._map)
    
    def to_ndarray(self) -> numpy.ndarray:
        """内部の ndarray を取得"""
        return self._map

    def rotate_right90(self, times: int):
        return TilesMap( numpy.rot90(self.to_ndarray().copy(), times) )

    def rotate(self, rotation: Rotation):
        rotation_times = 0
        if rotation == Rotation.RIGHT_90: rotation_times = 1
        elif rotation == Rotation.RIGHT_180: rotation_times = 2
        elif rotation == Rotation.RIGHT_270: rotation_times = 3
        
        return self.rotate_right90(rotation_times)

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

    from .pieces_shape import SHAPES

    def __init__(self, shape: TilesMap):
        self.shape = shape
        self.position: Tuple[int, int] | None = None
    
    @staticmethod
    def get_piece_set():
        return tuple(Piece( TilesMap(s) ) for s in Piece.SHAPES)
