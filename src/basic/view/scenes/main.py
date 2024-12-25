from ..view import View, Area
from .quad import PlayersType, SingleplayGameScene
from .title import TitleScene
from .game_setting import GameSettingScene

import pyxel

class MainView(View, Area):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        PT = PlayersType
        self.scene: View = TitleScene(x, y, w, h, self.hdl_select_singleplay)
    
    def hdl_select_singleplay(self):
        self.scene = GameSettingScene(self.x, self.y, self.w, self.h, lambda _: self.hdl_launch_singleplay())
    
    def hdl_launch_singleplay(self):
        PT = PlayersType
        self.scene = SingleplayGameScene(
            self.x, self.y, self.w, self.h,
            [
                (PT.AI, 'P1'),
                (PT.PLAYABLE, 'YOU'),
                (PT.AI, 'P2'),
                (PT.AI, 'P3'),
            ]
        )
    
    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
