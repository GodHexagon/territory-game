from typing import *
import enum

from numpy import ndarray as NDArray
import numpy

from .data import Rotation, GameData, TilesMap, Piece, PiecesBP
from .placement import PlacementRuleMap, PlacementResult

class Rule:
    """ゲームルールに基づきデータをアップデートさせ、さらに現在のデータを提供する"""
    BOARD_SIZE_TILES = 20

    def set_up(
            self, 
            players_number: int,
            start_corner: List[Tuple[bool, bool]]
        ):
        """子クラスのコンストラクタ内で実行すべきコストラクタ処理"""
        if not len(start_corner) == players_number: ValueError('start_corner引数が不正。プレイヤーの数だけリスト要素が存在している必要があります。')

        self.data = GameData(
            0,
            [Piece.get_piece_set() for _ in range(players_number)],
            start_corner,
            Rule.BOARD_SIZE_TILES
        )
        self.players_state = [0 for _ in range(players_number)] # 0: 一つもピースを置いていない, 1: 通常の状態, 2: 全てのピースを置いた
        self.logger = EventLogger(self.data)

        self.prm = PlacementRuleMap.get_empty_pm(self.data)
    
    def place(self, shape: TilesMap, rotation: Rotation, x: int, y: int):
        """プレイヤーがピースを置く操作"""
        selectables = tuple(p for p in self.data.pieces_by_player[self.get_turn()] if not p.placed() and shape.is_equal(p.shape))

        if len(selectables) == 0: raise ValueError('shapeが指し示すピースは、存在しない形状か、すでに全て置かれている。')
        
        target = selectables[0]
        
        future = target.copy()
        future.place(x, y, rotation)

        if self.players_state[self.get_turn()] == 0: c = self.data.start_corner[self.get_turn()]
        else: c = None
        result = self.prm.check(future, c)

        if not PlacementResult.successes(result): return result, self.__get_log()

        target.place(x, y, rotation)

        changed = self.get_turn()
        self.__switch_turn()
        self.logger.changed_piece_by_player.add(changed)

        return result, self.__get_log()
    
    def ai_place(self) -> Tuple[bool, 'EventLogger']:
        import random

        cand_shapes = list(p.shape for p in self.data.pieces_by_player[self.get_turn()] if not p.placed())
        random.shuffle(cand_shapes)

        for s in cand_shapes:
            cand_placements = []
            for r in (Rotation.DEFAULT, Rotation.RIGHT_90, Rotation.RIGHT_180, Rotation.RIGHT_270):
                cand_placements += self.find_placements(s, r)
            
            if not cand_placements.__len__() == 0: break
        else:
            _, ev = self.give_up()
            return False, ev

        randomed_placement = random.choice(cand_placements)
        pr, ev = self.place(*randomed_placement)

        if pr != PlacementResult.SUCCESS: raise RuntimeError('AIがピースの設置に失敗した。')

        return True, ev
        
    def give_up(self) -> Tuple[bool, 'EventLogger']:
        """ピースを置く場所がなくなったプレイヤーが、ピースを置く代わりに実行する。"""        
        target = self.get_turn()

        if self.players_state[target] == 2: return False, self.__get_log()

        self.players_state[target] = 2
        self.__switch_turn()
        self.logger.gave_up_player.add(target)

        return True, self.__get_log()
    
    def __switch_turn(self):
        """ターンを次へめくる"""
        turn = self.get_turn()
        if self.players_state[turn] != 2:
            if all( tuple(not p.placed() for p in self.data.pieces_by_player[turn]) ): self.players_state[turn] = 0
            elif all( tuple(p.placed() for p in self.data.pieces_by_player[turn]) ): self.players_state[turn] = 2
            else: self.players_state[turn] = 1

        pn = self.get_player_number()
        active_players = tuple(
            (self.get_turn() + i + 1) % pn
            for i in range(self.players_state.__len__())
            if self.players_state[(self.get_turn() + i + 1) % pn] != 2
        )

        if len(active_players) == 0:
            self.data.turn = GameData.END_STATE_TURN
            self.logger.ended = True
        else:
            self.data.turn = active_players[0]
            self.prm = PlacementRuleMap.get_current_pm(self.data)
    
    def __get_log(self):
        curr = self.logger
        self.logger = EventLogger(self.data)
        return curr

    def get_scores(self) -> List[int]:
        scores = []
        for pbp in self.data.pieces_by_player:
            scores.append( sum(tuple( p.count_tiles() for p in pbp if p.placed() )) )
        return scores
        
    def get_player_number(self):
        return len(self.data.pieces_by_player)

    def get_turn(self):
        return self.data.turn
    
    def get_pieces_shape(self, which_player: int):
        return tuple(p.shape for p in self.data.pieces_by_player[which_player])
    
    def is_end(self):
        return self.get_turn() == GameData.END_STATE_TURN
    
    def find_placements(self, shape: TilesMap, rotation: Rotation):
        candidates: List[Tuple[TilesMap, Rotation, int, int]] = []

        r = rotation
        piece = Piece(shape)
        _map = numpy.array( [[0 for _ in range(self.data.board_size)] for _ in range(self.data.board_size)] )
        for (y, x), _ in numpy.ndenumerate(_map):
            piece.place(x, y, r)
            
            if self.players_state[self.get_turn()] == 0: c = self.data.start_corner[self.get_turn()]
            else: c = None
            result = self.prm.check(piece, c)

            if PlacementResult.successes(result):
                candidates.append( (piece.shape, r, x, y) )
        return candidates

class Rule4Player(Rule):
    def __init__(self):
        self.set_up(
            4,
            [
                (False, True),
                (False, False),
                (True, False),
                (True, True),
            ]
        )
    
class EventLogger:
    def __init__(self, data: GameData):
        self.data = data
        self.changed_piece_by_player: Set[int] = set()
        self.gave_up_player: Set[int] = set()
        self.ended: bool = False
    
    def append(self, other: 'EventLogger'):
        self.changed_piece_by_player |= other.changed_piece_by_player
        self.gave_up_player |= other.gave_up_player
        self.ended |= other.ended
