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

        #self.tmp_board_map = numpy.array( [[0 for _ in range(self.data.board_size)] for _ in range(self.data.board_size)] )
        self.prm = PlacementRuleMap.get_empty_pm(self.data)
    
    def place(self, shape: TilesMap, rotation: Rotation, x: int, y: int) -> 'PlacementResult':
        selectable = self.data.pieces_by_player[self.data.turn]

        found = [p for p in selectable if shape.is_equal(p.shape)]
        if len(found) == 0: raise ValueError('shapeが指し示すピースがゲームに存在しない。')
        if len(found) > 1: assert False, "'.rule.rule.Piece.SHAPES'に、複数の同じ形状のピースが定義されている。"
        target = found[0]

        if target.placed(): raise ValueError('shapeが指し示すピースは、すでに盤上にある。')

        future = target.copy()
        future.place(x, y, rotation)
        result = self.prm.check(future)
        if not PlacementResult.successes(result): return result

        target.place(x, y, rotation)
        self.prm = PlacementRuleMap.get_next_pm(self.data)

        changed = self.get_turn()
        self.data.turn = (self.get_turn() + 1) % len(self.data.pieces_by_player)
        self.on_change_pieces(changed, self.data)

        return result
    
    def get_turn(self):
        return self.data.turn
    
    def get_pieces_shape(self, which_player: int):
        return tuple(p.shape for p in self.data.pieces_by_player[which_player])

class PlacementResult(enum.Enum):
    SUCCESS = 0
    COLLISION = 1
    SURFACE = 2
    CORNER = 3
    OUT_OF_BOARD = 4
    
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
    def get_next_pm(data: 'GameData', turn: Optional[int] = None):
        if turn is None: turn = (data.turn + 1) % len(data.pieces_by_player)

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

        cor = False

        shape = piece.get_rotated_shape()
        for (y, x), value in numpy.ndenumerate(shape.to_ndarray()):
            if value in (Piece.TILED, Piece.CENTER):
                px, py = piece.get_pos()
                tx = px + x
                ty = py + y
                
                def is_in_range(value: int):
                    return 0 <= value and value < Rule.BOARD_SIZE_TILES

                if not is_in_range(tx) or not is_in_range(ty): return PlacementResult.OUT_OF_BOARD
                if self.col[ty][tx]: return PlacementResult.COLLISION
                if self.sur[ty][tx]: return PlacementResult.SURFACE

                cor = cor or self.cor[ty][tx]
        
        if not cor: return PlacementResult.CORNER
        
        return PlacementResult.SUCCESS

class RuleVSAI(Rule):
    PLAYER = 0
    AI = 1
    def __init__(self, on_change_pieces: Callable[[int, 'GameData'], None]):
        self.set_up(2, on_change_pieces)

        self.data.pieces_by_player[0][0].place(0, self.data.board_size - 1, Rotation.DEFAULT)
        self.data.pieces_by_player[1][0].place(0, 0, Rotation.DEFAULT)
        self.prm = PlacementRuleMap.get_next_pm(self.data, 0)
        self.on_change_pieces(0, self.data)
        self.on_change_pieces(1, self.data)
    
    def place(self, shape, rotation, x, y):
        if self.data.turn == RuleVSAI.AI: raise RuntimeError('ゲームのターンが不正。')

        result = super().place(shape, rotation, x, y)
        if not PlacementResult.successes(result): return result

        import random

        randomed_shape = random.choice( tuple(p.shape for p in self.data.pieces_by_player[RuleVSAI.AI] if not p.placed()) )
        candidates = self.__get_candidate_placements(randomed_shape)
        randomed_placement = random.choice(candidates)
        super().place(*randomed_placement)

        return result
    
    def __get_candidate_placements(self, shape: TilesMap):
        candidates: List[Tuple[TilesMap, Rotation, int, int]] = []

        piece = Piece(shape)
        for r in (Rotation.DEFAULT, Rotation.RIGHT_90, Rotation.RIGHT_180, Rotation.RIGHT_270):
            _map = numpy.array( [[0 for _ in range(self.data.board_size)] for _ in range(self.data.board_size)] )
            for (y, x), _ in numpy.ndenumerate(_map):
                piece.place(x, y, r)
                if PlacementResult.successes(self.prm.check(piece)):
                    candidates.append([piece.shape.copy(), r, x, y])
        
        return candidates

if __name__ == '__main__':
    d = GameData(
        0,
        [Piece.get_piece_set() for _ in range(2)],
        Rule.BOARD_SIZE_TILES
    )
    m = PlacementRuleMap.get_empty_pm(d)
    print(m.cor)
