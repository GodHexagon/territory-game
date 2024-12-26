from .game import GameScene
from ..player_type import PlayerType
from pyxres import BLUE_COLOR_S, RED_COLOR_S, GREEN_COLOR_S, YELLOW_COLOR_S
from ....rule.rule import GameData, PlacementResult, EventLogger, Rule, BasicRule, Rotation, TilesMap

from typing import *

class MultiplayerGameScene(GameScene):
    def __init__(self, x, y, w, h, 
        players_data: List[Tuple[str, PlayerType]],
    ) -> None:
        super().__init__(x, y, w, h)
        self.init_view(0, BasicRule(2, [(False, False), (True, True)]).get_pieces_shape(0))
    
    def update(self):
        pass
    
    def draw(self):
        pass

    def hdl_give_up(self):
        pass
    
    def hdl_place_piece(self, shape, rotation, x, y):
        pass