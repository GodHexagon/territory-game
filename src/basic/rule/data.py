from typing import *
import enum

from numpy.typing import *
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
        
        # int 型であることを確認
        if not numpy.issubdtype(input_array.dtype, numpy.integer):
            raise ValueError("TileMap only supports arrays with integer values.")
        
        self._map = input_array
        self.height, self.width = input_array.shape

    def copy(self):
        return TilesMap(self.to_ndarray())
    
    def to_ndarray(self) -> NDArray[numpy.int_]:
        """内部の ndarray を取得"""
        return self._map.copy()

    def rotate_right90(self, times: int):
        return TilesMap( numpy.rot90(self.to_ndarray(), times) )

    def rotate(self, rotation: Rotation):
        rotation_times = 0
        if rotation == Rotation.RIGHT_90: rotation_times = 3
        elif rotation == Rotation.RIGHT_180: rotation_times = 2
        elif rotation == Rotation.RIGHT_270: rotation_times = 1
        
        return self.rotate_right90(rotation_times)

    def is_equal(self, other: 'TilesMap') -> bool:
        """
        他の TilesMap と配列が等しいかを判定します。

        Parameters:
            other (TilesMap): 比較対象の TilesMap オブジェクト。

        Returns:
            bool: 配列が等しい場合は True、異なる場合は False。
        """
        if not isinstance(other, TilesMap):
            return False
        return numpy.array_equal(self._map, other._map)
    
PiecesBP: TypeAlias =Tuple['Piece']

class GameData:
    """ゲーム進行状況を維持する最低限のデータ"""
    def __init__(self, turn: int, pieces_by_player: List[PiecesBP], board_size: int):
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

    def __init__(self, shape: TilesMap, position: Optional['PiecePosition'] = None):
        self.shape = shape
        self.position = position
    
    @staticmethod
    def get_piece_set():
        return tuple(Piece( TilesMap(s) ) for s in Piece.SHAPES)
    
    def placed(self):
        return self.position is not None
    
    def get_rotated_shape(self) -> TilesMap | None:
        if self.position is None: return None
        return self.shape.rotate(self.position.rotation)
        
    def place(self, x, y, rotation):
        self.position = PiecePosition(x, y , rotation)
    
    def copy(self):
        return Piece(self.shape, self.position)

class PiecePosition:
    def __init__(self, x: int, y: int, rotation: Rotation):
        self.x, self.y, self.rotation = x, y, rotation
