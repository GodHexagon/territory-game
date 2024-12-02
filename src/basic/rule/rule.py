from typing import *
import enum

from numpy import ndarray as NDArray
import numpy

from .data import Rotation, GameData, TilesMap, Piece

class Rule:
    """ゲームルールに基づきデータをアップデートさせ、さらに現在のデータを提供する"""
    BOARD_SIZE_TILES = 20

    def set_up(
            self, players_number: int, on_change_players_pieces: Callable[]):
        self.data = GameData(
            0,
            [Piece.get_piece_set() for _ in range(players_number)],
            Rule.BOARD_SIZE_TILES
        )
        self.tmp_board_map = numpy.array( [[0 for _ in range(self.data.board_size)] for _ in range(self.data.board_size)] )
        self.next_pm = PlacementRuleMap.get_empty_pm(self.data)
    
    def place(self, shape: TilesMap, rotation: Rotation, x: int, y: int) -> 'PlacementResult':
        selectable = self.data.pieces_by_player[self.data.turn]

        found = [p for p in selectable if shape.is_equal(p.shape)]
        if len(found) == 0: raise ValueError('shapeが指し示すピースがゲームに存在しない。')
        if len(found) > 1: assert False, "'.rule.rule.Piece.SHAPES'に、複数の同じ形状のピースが定義されている。"
        target = found[0]

        if target.placed(): raise ValueError('shapeが指し示すピースは、すでに盤上にある。')

        future = target.copy()
        future.place(x, y, rotation)
        result = self.next_pm.check(future)
        if not PlacementResult.successes(result): return result

        target.place(x, y, rotation)
        self.data.turn = (self.data.turn + 1) % len(self.data.pieces_by_player)
        return result
    
    def get_turn(self):
        return self.data.turn
    
    def get_pieces_shape(self, which_player: int):
        return tuple(p.shape for p in self.data.pieces_by_player[which_player])

class PlacementResult(enum.Enum):
    SUCCESS = 0
    
    @staticmethod
    def successes(value: 'PlacementResult'):
        return value == PlacementResult.SUCCESS

class PlacementRuleMap:
    def __init__(self, col: NDArray, sur: NDArray, cor: NDArray):
        self.col = col
        self.sur = sur
        self.cor = cor
    
    @staticmethod
    def get_empty_pm(data: 'GameData'):
        empty_map = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        return PlacementRuleMap(empty_map, empty_map, empty_map)

    """@staticmethod
    def get_next_pm(data: 'GameData'):
        col = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        sur = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        cor = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        
        for pieces in data.pieces_by_player:
            corner_rule = pieces is data.pieces_by_player[data.turn]
            for p in pieces:
                pass

        return PlacementRuleMap(
            
        )"""

    def check(self, piece: TilesMap) -> PlacementResult:
        return PlacementResult.SUCCESS

class RuleVSAI(Rule):
    PLAYER = 0
    AI = 1
    def __init__(self):
        self.set_up(2)


if __name__ == '__main__':
    pass
