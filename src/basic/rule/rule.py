from typing import *
import enum

from numpy import ndarray as NDArray
import numpy

from .data import Rotation, GameData, TilesMap, Piece, PiecesBP
from .placement import PlacementRuleMap, PlacementResult

class Rule:
    """ゲームルールに基づきデータをアップデートさせ、さらに現在のデータを提供する"""
    BOARD_SIZE_TILES = 20

    def set_on_change_pieces(self, value: Callable[[int, 'GameData'], None]):
        self.on_change_pieces = value
    
    def set_on_end(self, value: Callable[[], None]):
        self.on_end = value
    
    def set_on_give_up(self, value: Callable[[int], None]):
        self.on_give_up = value

    def set_up(
            self, 
            players_number: int,
            start_corner: List[Tuple[bool, bool]]
        ):
        if not len(start_corner) == players_number: ValueError('start_corner引数が不正。プレイヤーの数だけリスト要素が存在している必要があります。')

        self.data = GameData(
            0,
            [Piece.get_piece_set() for _ in range(players_number)],
            start_corner,
            Rule.BOARD_SIZE_TILES
        )
        self.players_state = [0 for _ in range(players_number)] # 0: 一つもピースを置いていない, 1: 通常の状態, 2: 全てのピースを置いた

        self.prm = PlacementRuleMap.get_empty_pm(self.data)
    
    def place(self, shape: TilesMap, rotation: Rotation, x: int, y: int, turn: Optional[int] = None) -> 'PlacementResult':
        if turn is not None and turn != self.get_turn(): return PlacementResult.OTHERS_TURN

        selectable = self.data.pieces_by_player[self.get_turn()]

        found = [p for p in selectable if shape.is_equal(p.shape)]
        if len(found) == 0: raise ValueError('shapeが指し示すピースがゲームに存在しない。')
        if len(found) > 1: assert False, "'.rule.rule.Piece.SHAPES'に、複数の同じ形状のピースが定義されている。"
        target = found[0]

        if target.placed(): raise ValueError('shapeが指し示すピースは、すでに盤上にある。')

        
        future = target.copy()
        future.place(x, y, rotation)

        if self.players_state[self.get_turn()] == 0: c = self.data.start_corner[self.get_turn()]
        else: c = None
        result = self.prm.check(future, c)

        if not PlacementResult.successes(result): return result

        target.place(x, y, rotation)

        changed = self.get_turn()
        self.switch_turn()
        self.on_change_pieces(changed, self.data)

        return result
    
    def switch_turn(self):
        turn = self.get_turn()
        if self.players_state[turn] != 2:
            if all( tuple(not p.placed() for p in self.data.pieces_by_player[turn]) ): self.players_state[turn] = 0
            elif all( tuple(p.placed() for p in self.data.pieces_by_player[turn]) ): self.players_state[turn] = 2
            else: self.players_state[turn] = 1

        if all( tuple(s == 2 for s in self.players_state) ): self.on_end()

        pn = self.get_player_number()

        active_players = tuple(
            (self.get_turn() + i + 1) % pn
            for i in range(self.players_state.__len__())
            if self.players_state[(self.get_turn() + i + 1) % pn] != 2
        )

        if len(active_players) == 0:
            self.on_end()
        else:
            self.data.turn = active_players[0]
            self.prm = PlacementRuleMap.get_current_pm(self.data)
        
    def get_player_number(self):
        return len(self.data.pieces_by_player)

    def give_up(self, player: int):
        self.players_state[player] = 2
        self.switch_turn()
        self.on_give_up(player)

    def get_turn(self):
        return self.data.turn
    
    def get_pieces_shape(self, which_player: int):
        return tuple(p.shape for p in self.data.pieces_by_player[which_player])


class RuleVSAI(Rule):
    PLAYER = 0
    AI = 1
    def __init__(self):
        self.set_up(2, [(False, True), (True, False)])
    
    def place(self, shape: TilesMap, rotation: Rotation, x: int, y: int, _: Optional[int] = None) -> 'PlacementResult':
        result = super().place(shape, rotation, x, y, RuleVSAI.PLAYER)
        if result == PlacementResult.OTHERS_TURN: raise RuntimeError('ターンが不正。')

        while(self.get_turn() == RuleVSAI.AI):
            self.__ai_place()

        return result
    
    def __ai_place(self):
        import random

        cand_shapes = list(p.shape for p in self.data.pieces_by_player[self.get_turn()] if not p.placed())
        random.shuffle(cand_shapes)

        for s in cand_shapes:
            cand_placements = self.__get_candidate_placements(s)
            if not cand_placements.__len__() == 0: break
        else:
            self.give_up(RuleVSAI.AI)
            return

        randomed_placement = random.choice(cand_placements)
        ai_result = super().place(*randomed_placement, RuleVSAI.AI)

        if not PlacementResult.successes(ai_result): raise RuntimeError('AIがピースの設置に失敗した。')
    
    def __get_candidate_placements(self, shape: TilesMap):
        candidates: List[Tuple[TilesMap, Rotation, int, int]] = []

        piece = Piece(shape)
        for r in (Rotation.DEFAULT, Rotation.RIGHT_90, Rotation.RIGHT_180, Rotation.RIGHT_270):
            _map = numpy.array( [[0 for _ in range(self.data.board_size)] for _ in range(self.data.board_size)] )
            for (y, x), _ in numpy.ndenumerate(_map):
                piece.place(x, y, r)
                
                if self.players_state[self.get_turn()] == 0: c = self.data.start_corner[self.get_turn()]
                else: c = None
                result = self.prm.check(piece, c)

                if PlacementResult.successes(result):
                    candidates.append( (piece.shape, r, x, y) )
        
        return candidates

if __name__ == '__main__':
    pass
