from typing import *
import enum

from numpy import ndarray as NDArray
import numpy

from .data import Rotation, GameData, TilesMap, Piece, PiecesBP

class Rule:
    """ゲームルールに基づきデータをアップデートさせ、さらに現在のデータを提供する"""
    BOARD_SIZE_TILES = 20

    def set_up(
            self, 
            players_number: int,
            on_change_pieces: Callable[[int, 'GameData'], None]
        ):
        self.data = GameData(
            0,
            [Piece.get_piece_set() for _ in range(players_number)],
            Rule.BOARD_SIZE_TILES
        )
        self.on_change_pieces = on_change_pieces

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
        self.next_pm = PlacementRuleMap.get_next_pm(self.data)

        changed = self.get_turn()
        self.data.turn = (self.data.turn + 1) % len(self.data.pieces_by_player)
        self.on_change_pieces(changed, self.data)

        return result
    
    def get_turn(self):
        return self.data.turn
    
    def get_pieces_shape(self, which_player: int):
        return tuple(p.shape for p in self.data.pieces_by_player[which_player])

class PlacementResult(enum.Enum):
    SUCCESS = 0
    COLISION = 1
    SURFACE = 2
    CORNER = 3
    
    @staticmethod
    def successes(value: 'PlacementResult'):
        return value == PlacementResult.SUCCESS

class PlacementRuleMap:
    def __init__(self, col: NDArray, sur: NDArray, cor: NDArray):
        self.col = col # colision rule map
        self.sur = sur # surface rule map
        self.cor = cor # corner rule map
    
    @staticmethod
    def get_empty_pm(data: 'GameData'):
        empty_map = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        return PlacementRuleMap(empty_map, empty_map.copy(), empty_map.copy())

    @staticmethod
    def get_next_pm(data: 'GameData'):
        col = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        sur = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )
        cor = numpy.array( [[False for _ in range(data.board_size)] for _ in range(data.board_size)] )

        def put(map: NDArray, x, y):
            SIZE = data.board_size
            target = data.limit_in_board( (x, y) )
            map[target[0], target[1]] = True
        
        for pieces in data.pieces_by_player:
            enabled_corner_rule = pieces is data.pieces_by_player[data.turn]
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

        return PlacementRuleMap(col, sur, cor)

    def check(self, piece: Piece) -> PlacementResult:
        if not piece.placed(): raise ValueError('ピースが設置されていない。')

        col = True
        sur = True
        cor = False

        shape = piece.get_rotated_shape()
        for (y, x), value in numpy.ndenumerate(shape.to_ndarray()):
            if value in (Piece.TILED, Piece.CENTER):
                px, py = piece.get_pos()

                col = col and not self.col[px + x][py + y]
                sur = sur and not self.sur[px + x][py + y]
                cor = cor or self.cor[px + x][py + y]
        
        if not col: return PlacementResult.COLISION
        if not sur: return PlacementResult.SURFACE
        if not cor: return PlacementResult.CORNER
        
        return PlacementResult.SUCCESS

class RuleVSAI(Rule):
    PLAYER = 0
    AI = 1
    def __init__(self, on_change_pieces: Callable[[int, 'GameData'], None]):
        self.set_up(2, on_change_pieces)

        self.data.pieces_by_player[0][0].place(0, self.data.board_size - 1, Rotation.DEFAULT)
        self.data.pieces_by_player[1][0].place(0, 0, Rotation.DEFAULT)
        self.next_pm = PlacementRuleMap.get_next_pm(self.data)
        self.on_change_pieces(0, self.data)
        self.on_change_pieces(1, self.data)
    
    def place(self, shape, rotation, x, y):
        if self.data.turn == RuleVSAI.AI: raise RuntimeError('ゲームのターンが不正。')

        result = super().place(shape, rotation, x, y)
        if not PlacementResult.successes(result): return result

        unplaced_piece = tuple(q for q in self.data.pieces_by_player[RuleVSAI.AI] if not q.placed())[0]
        super().place(unplaced_piece.shape, 0, 0, 0)

        return result

if __name__ == '__main__':
    d = GameData(
        0,
        [Piece.get_piece_set() for _ in range(2)],
        Rule.BOARD_SIZE_TILES
    )
    m = PlacementRuleMap.get_empty_pm(d)
    print(m.cor)
