from ...areas.text import WritenText
from ...base.limitter import LimitableArea
from ..player_type import PlayerType
from ....data.player_color import PLAYER_COLORS
from ...base.view import View, Area
from src.pyxres import *

from typing import *

import pyxel

class SceneData:
    ROW_HEIGHT_PX = 56
    ROW_GAP_PX = 8

    LIST_WIDTH_PX = 512
    
    PLAYER_COLORS = PLAYER_COLORS

class Lobby(View, Area):
    def __init__(self,
        x: float, y: float, w: float, h: float,
        on_cancel: Callable[[], None],
        player_data: List[Tuple[str, PlayerType]]
    ):
        if not (x == 0 and y == 0): raise ValueError('このAreaは画面サイズ依存です。')
        self.init_area(x, y, w, h)

        # プレイヤー表（行）
        PW = SceneData.LIST_WIDTH_PX
        PCS = SceneData.PLAYER_COLORS
        RH = SceneData.ROW_HEIGHT_PX
        RG = SceneData.ROW_GAP_PX

        l: List[Player] = []
        for i, color, color_name in PCS:
            player = Player(
                x + (w - PW) / 2,
                y + i * (RH + RG) + 128,
                PW,
                color_name,
                color,
                lambda _: None,
                default=PlayerType.PLAYABLE if i == 0 else PlayerType.AI
            )
            l.append(player)
        self.players = l
    
    def update(self):
        pass

    def draw(self):
        pyxel.cls(COLOR_WHITE)
        for p in self.players:
            p.draw()


class Player(LimitableArea):
    HEIGHT_PX = SceneData.ROW_HEIGHT_PX

    def __init__(self, x, y, w, 
            label: str, 
            label_color: int, 
            on_change: Callable[[PlayerType], None], 
            default: PlayerType = PlayerType.AI
        ):
        super().init_area(x, y, w, Player.HEIGHT_PX)
        self.set_limiteds()

        self.on_change = on_change
        self.type = default

        self.label = WritenText(0, y + self.h / 2, label, label_color, scale=3)
        self.label.x = x + 16
    
    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()
