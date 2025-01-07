from ..base.view import View, Area
from .game.singleplayer import SingleplayGameScene
from .game.multiplayer import MultiplayerGameScene
from .title.title import TitleScene
from .game_setting.game_setting import GameSettingScene
from .akst.akst import AccessKeySettingScene
from .player_type import PlayerType

from typing import *

class MainView(View, Area):
    def __init__(self, x, y, w, h):
        super().init_area(x, y, w, h)
        self.__show_title()
    
    def __show_title(self):
        self.scene: View = TitleScene(self.x, self.y, self.w, self.h,
            lambda : self.__show_game_setting(False),
            lambda : self.__show_game_setting(True),
            lambda : self.__show_access_key_setting()
        )
    
    def __show_access_key_setting(self):
        self.scene = AccessKeySettingScene(self.x, self.y, self.w, self.h,
            lambda ok: self.__show_title()
        )
    
    def __show_game_setting(self, multiplayer: bool):
        self.scene = GameSettingScene(self.x, self.y, self.w, self.h, 
            lambda players: self.__launch_game(players),
            lambda : self.__show_title(),
            multiplay=multiplayer
        )
    
    def __launch_game(self, players: List[Tuple[str, PlayerType]]):
        multiplayer = False
        for _, type in players:
            if type == PlayerType.MULTIPLAYER: multiplayer = True

        if multiplayer:
            self.scene = MultiplayerGameScene(
                self.x, self.y, self.w, self.h, players
            )
        else: 
            self.scene = SingleplayGameScene(
                self.x, self.y, self.w, self.h, players
            )
    
    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
