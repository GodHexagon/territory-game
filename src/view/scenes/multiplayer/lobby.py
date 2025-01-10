from ...areas.text import WritenText
from ...base.limitter import LimitableArea
from ..player_type import PlayerType
from ....data.player_color import PLAYER_COLORS
from ...base.view import View, Area
from ...areas.button import TextButton
from src.pyxres import *

from typing import *

import pyxel

class SceneData:
    ROW_HEIGHT_PX = 56
    ROW_GAP_PX = 8

    LIST_WIDTH_PX = 512
    
    PLAYER_COLORS = PLAYER_COLORS

    LIST_X_GAP_PX = 16

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

        if len(PCS) != len(player_data): raise ValueError("player_dataの要素数は想定されるプレイヤー数の分だけ必要。")

        l: List[Player] = []
        current_y = 128
        for (_, color, _), (name, pt)in zip(PCS, player_data):
            if pt == PlayerType.UNASSIGNED: continue

            player = Player(
                x + (w - PW) / 2,
                current_y,
                PW,
                name,
                color,
                pt
            )

            current_y = current_y + RH + RG

            l.append(player)

        self.players = l

        # キャンセルボタン
        self.cancel_b = TextButton(
            x + w / 2, y + 128 + (RH + RG) * len(self.players) + 32, label="CANCEL",
            on_click=lambda : on_cancel()
        )
    
    def update(self):
        self.cancel_b.update()

    def draw(self):
        pyxel.cls(COLOR_WHITE)
        for p in self.players:
            p.draw()
        self.cancel_b.draw()


class Player(LimitableArea):
    HEIGHT_PX = SceneData.ROW_HEIGHT_PX

    def __init__(self, x, y, w, 
            label: str, 
            label_color: int,
            pt: PlayerType
        ):
        super().init_area(x, y, w, Player.HEIGHT_PX)
        self.set_limiteds()

        GAP = SceneData.LIST_X_GAP_PX

        self.label = WritenText(0, y + self.h / 2, label, label_color, scale=3)
        self.label.x = x + GAP
        
        if pt == PlayerType.PLAYABLE: 
            status = "YOU"
            c = COLOR_BLACK
        elif pt == PlayerType.AI: 
            status = "AI"
            c = COLOR_BLACK
        else: 
            status = "WAITING..."
            c = COLOR_FAILURE
        self.status = WritenText(0, y + self.h / 2, status, c, scale=3)
        self.status.to_x(x + GAP + self.label.x)
    
    def joined(self):
        self.status.rewrite("CONNECTED!", COLOR_SUCCESSFULL)
    
    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()
        self.status.draw()
