from ...base.view import View, Area
from ..game_setting.multiplayer import MultiplayerGameSettingScene
from .lobby import Lobby
from ..player_type import PlayerType

from typing import *

import pyxel 

class HostScene(View, Area):
    def __init__(self,
        x: float, y: float, w: float, h: float,
        on_cancel: Callable[[], None]
    ):
        self.init_area(x, y, w, h)
        
        self.on_cancel = on_cancel
        
        self.show_setting()
    
    def show_setting(self):
        self.scene: View = MultiplayerGameSettingScene(
            self.x, self.y, self.w, self.h,
            self.show_lobby,
            self.on_cancel
        )
    
    def show_lobby(self, data: List[Tuple[str, PlayerType]]):
        self.scene = Lobby(self.x, self.y, self.w, self.h, self.show_setting, data)

    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
