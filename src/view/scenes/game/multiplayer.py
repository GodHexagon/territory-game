from .game import GameScene
from ..player_type import PlayerType
from src.pyxres import BLUE_COLOR_S, RED_COLOR_S, GREEN_COLOR_S, YELLOW_COLOR_S
from ....rule.rule import GameData, PlacementResult, EventLogger, Rule, BasicRule, Rotation, TilesMap

from typing import *

class MultiplayerGameScene(GameScene):
    def __init__(self, x, y, w, h, 
        players_data: List[Tuple[str, PlayerType]],
    ) -> None:
        inidif = (
            ((False, True), BLUE_COLOR_S),
            ((False, False), RED_COLOR_S),
            ((True, False), GREEN_COLOR_S),
            ((True, True), YELLOW_COLOR_S),
        )

        if players_data.__len__() != 4: raise ValueError(f'players_data引数の要素数は必ず4です。{players_data.__len__()}')

        playable_id = None
        players: List[Tuple[str, int]] = []
        corners: List[Tuple[bool, bool]] = []
        for (name, type), (corner, color)in zip(players_data, inidif):
            if type != PlayerType.UNASSIGNED:
                if type == PlayerType.PLAYABLE: playable_id = players.__len__()

                players.append((name, color))
                corners.append(corner)
        else:
            if playable_id is None: raise ValueError('プレイヤーのidが指定されていません。')
        
        if players.__len__() == 2:
            corners = [inidif[0][0], inidif[2][0]]

        self.playable_id = playable_id
        self.players = players
        
        self.game: Rule = BasicRule(
            players.__len__(),
            corners
        )

        super().init_area(x, y, w, h)
        self.init_view(self.players[self.playable_id][1], self.game.get_pieces_shape(self.playable_id))

        self.__turn_end()
    
    def __turn_end(self, log: Optional[EventLogger] = None) -> None:
        while self.game.get_turn() != self.playable_id and not self.game.is_end():
            _, l = self.game.ai_place()
            if log is None: log = l
            else: log.append(l)
        
        if log is not None: self.__commmon_event_handler(log)
    
    def __commmon_event_handler(self, log: EventLogger) -> None:
        data = log.data

        cpbp = log.changed_piece_by_player
        if cpbp.__len__() > 0: 
            if self.playable_id in cpbp:
                self.picker.reset_pieces(
                    tuple(p.shape for p in data.pieces_by_player[self.playable_id] if not p.placed())
                )
                held = self.cursor.held
                if held is not None:
                    held.clear()
            self.board.rewrite_board(tuple(data.pieces_by_player.copy()), tuple(c for _, c in self.players))
        
        g_p = log.gave_up_player
        if g_p.__len__() == 1:
            name, color = self.players[g_p.pop()]
            self.notice.put(f'{name} GAVE UP!', color=color)
        elif g_p.__len__() > 1:
            self.notice.put('SOME PEOPLE GAVE UP!')
        
        if log.ended:
            scores = self.game.get_scores()
            ps = scores[self.playable_id]
            if any([s > ps for s in scores]): win = -1
            elif scores.count(ps) > 1: win = 0
            else: win = 1
            self.result.show(
                [(f"{name}: {score}", color) for (name, color), score in zip(self.players, scores)],
                win
            )
    
    def hdl_place_piece(self, shape: TilesMap, rotation: Rotation, x: int, y: int) -> bool:
        if self.game.get_turn() == GameData.END_STATE_TURN: return False
        if self.game.get_turn() != self.playable_id: raise RuntimeError('ターンが不正である。')

        success = False
        if self.game.get_turn() == self.playable_id:
            r, l = self.game.place(shape, rotation, x, y)
            success = r == PlacementResult.SUCCESS
            
            self.__turn_end(l)

        return success
    
    def hdl_give_up(self) -> bool:
        if self.game.get_turn() == self.playable_id:
            s, l = self.game.give_up()

            self.__turn_end(l)

            return s
        return False
    
    def update(self) -> None:        
        super().update()
