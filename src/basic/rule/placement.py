import enum
from typing import *

from numpy.typing import NDArray
import numpy

from .data import GameData, Piece

class PlacementResult(enum.Enum):
    SUCCESS = 0
    COLLISION_RULE_DENIAL = 1
    SURFACE_RULE_DENIAL = 2
    CORNER_RULE_DENIAL = 3
    OUT_OF_BOARD = 4
    FIRST_PIECE_RULE_DENIAL = 5
    OTHERS_TURN = 6
    
    @staticmethod
    def successes(value: 'PlacementResult'):
        return value == PlacementResult.SUCCESS

class PlacementRuleMap:
    def __init__(self, col: NDArray, sur: NDArray, cor: NDArray, board_size: int):
        self.col = col # colision rule map
        self.sur = sur # surface rule map
        self.cor = cor # corner rule map
        self.board_size = board_size
    
    @staticmethod
    def get_empty_pm(data: 'GameData'):
        empty_map = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        return PlacementRuleMap(empty_map, empty_map.copy(), empty_map.copy(), data.board_size)

    @staticmethod
    def get_current_pm(data: 'GameData', turn: Optional[int] = None):
        if turn is None: turn = data.turn

        col = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        sur = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        cor = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )

        def put(map: NDArray, x, y):
            if data.is_in_range( (x, y) ):
                map[y][x] = True
        
        for pieces in data.pieces_by_player:
            enabled_corner_rule = pieces is data.pieces_by_player[turn]
            for p in pieces:
                if not p.placed(): continue
                shape = p.get_rotated_shape()
                for (y, x), value in numpy.ndenumerate(shape.to_ndarray()):
                    if value in (Piece.TILED, Piece.CENTER):
                        px, py = p.get_pos()

                        put(
                            col,
                            px + x,
                            py + y
                        )

                        if enabled_corner_rule:
                            coords = (
                                (-1, 0),
                                (0, -1),
                                (1, 0),
                                (0, 1),
                            )
                            for ay, ax in coords:
                                put(
                                    sur,
                                    px + x + ax,
                                    py + y + ay
                                )
                        
                        if enabled_corner_rule:
                            coords = (
                                (-1, -1),
                                (1, -1),
                                (-1, 1),
                                (1, 1),
                            )
                            for ay, ax in coords:
                                put(
                                    cor,
                                    px + x + ax,
                                    py + y + ay
                                )

        return PlacementRuleMap(col, sur, cor, data.board_size)

    def check(self, piece: Piece, corner_pointer: Optional[Tuple[bool, bool]] = None) -> PlacementResult:
        if not piece.placed(): raise ValueError('ピースが設置されていない。')

        if corner_pointer is not None:
            if not corner_pointer[0]: allowed_x = 0
            else: allowed_x = self.board_size - 1
            if not corner_pointer[1]: allowed_y = 0
            else: allowed_y = self.board_size - 1
        else:
            allowed_x = -1
            allowed_y = -1

        cor = False
        fpr = False

        shape = piece.get_rotated_shape()
        for (y, x), value in numpy.ndenumerate(shape.to_ndarray()):
            if value in (Piece.TILED, Piece.CENTER):
                px, py = piece.get_pos()
                tx = px + x
                ty = py + y
                
                def is_in_range(value: int):
                    return 0 <= value and value < self.board_size

                if not is_in_range(tx) or not is_in_range(ty): return PlacementResult.OUT_OF_BOARD
                if self.col[ty][tx]: return PlacementResult.COLLISION_RULE_DENIAL
                if self.sur[ty][tx]: return PlacementResult.SURFACE_RULE_DENIAL

                cor = cor or self.cor[ty][tx]
                fpr = fpr or (tx == allowed_x and ty == allowed_y)
        
        if corner_pointer is not None:
            if fpr: return PlacementResult.SUCCESS
            else: return PlacementResult.FIRST_PIECE_RULE_DENIAL
        if cor: return PlacementResult.SUCCESS
        else: return PlacementResult.CORNER_RULE_DENIAL