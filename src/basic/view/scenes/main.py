from ..view import View, Area
from .quad import SingleplayGameScene
from .title import TitleScene
from .game_setting import GameSettingScene
from .player_type import PlayerType

from typing import *

class MainView(View, Area):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.scene: View = TitleScene(x, y, w, h, self.hdl_select_singleplay)
    
    def hdl_select_singleplay(self):
        self.scene = GameSettingScene(self.x, self.y, self.w, self.h, 
            lambda players: self.hdl_launch_singleplay(players)
        )
    
    def hdl_launch_singleplay(self, players: List[Tuple[str, PlayerType]]):
        self.scene = SingleplayGameScene(
            self.x, self.y, self.w, self.h, players
        )
    
    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
