from ...areas.text import WritenText
from ...base.limitter import LimitableArea
from ..player_type import PlayerType
from ....data.player_color import PLAYER_COLORS
from ...base.view import View, Area
from ...areas.button import TextButton, IconButton
from src.pyxres import *

from typing import *

import pyxel
import pyperclip # type: ignore

class SceneData:
    ROW_HEIGHT_PX = 56
    ROW_GAP_PX = 8

    LIST_WIDTH_PX = 512
    
    PLAYER_COLORS = PLAYER_COLORS

    LIST_X_GAP_PX = 16

    PASSWORD_WIDTH_PX = 128

class Lobby(View, Area):
    def __init__(self,
        x: float, y: float, w: float, h: float,
        on_cancel: Callable[[], None],
        player_data: List[Tuple[str, PlayerType]]
    ):
        if not (x == 0 and y == 0): raise ValueError('このAreaは画面サイズ依存です。')
        self.init_area(x, y, w, h)

        self.title = WritenText(x + w / 2, 64, "WAITING FOR PLAYERS", COLOR_FAILURE, scale=5)

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
        for p in self.players:
            p.update()
        self.cancel_b.update()

    def draw(self):
        pyxel.cls(COLOR_WHITE)
        self.title.draw()
        for p in self.players:
            p.draw()
        self.cancel_b.draw()


class Player(LimitableArea, View):
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

        self.pw = ReadonlyText("test")
        self.pw.to_center_pos(*self.get_center_pos())
        self.pw.to_x(x + w - GAP - SceneData.PASSWORD_WIDTH_PX)
        self.pw.set_w(SceneData.PASSWORD_WIDTH_PX)
    
    def joined(self):
        self.status.rewrite("CONNECTED!", COLOR_SUCCESSFULL)
    
    def update(self):
        self.pw.update()
    
    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()
        self.status.draw()
        self.pw.draw()
        
class ReadonlyText(Area):
    ICON_SIZE_PX = 24
    MARGIN_PX = 8
    GAP_PX = 8
    MIN_WIDTH = 128

    def __init__(self, text: str = ""):
        IS = ReadonlyText.ICON_SIZE_PX
        MARGIN = ReadonlyText.MARGIN_PX

        self.init_unplaced_area(self.MIN_WIDTH, IS + MARGIN * 2)

        self.text = text
        self.field = TextButton(0, 0, lambda: None, text)
        
        TX, TY = COPY_ICON_COOR
        self.copy_b = IconButton(
            0, 0, size=IS, on_click=self.__hdl_copy,
            tile_selector=(TX, TY, TILE_SIZE_PX, TILE_SIZE_PX)
        )

        self.set_colors()
    
    def get_text(self):
        return self.text
        
    def to_x(self, x):
        diff = x - self.x
        super().to_x(x)
        self.field.to_x(x + self.MARGIN_PX)
        self.copy_b.to_x(self.copy_b.x + diff)

    def to_y(self, y):
        super().to_y(y)
        self.field.to_y(y + ((self.MARGIN_PX * 2 + self.ICON_SIZE_PX) - self.field.h) / 2)
        self.copy_b.to_y(y + self.MARGIN_PX)
    
    def set_w(self, w):
        w = max(w, self.MIN_WIDTH)
        super().set_w(w)
        self.field.set_w(w - self.MARGIN_PX * 2 - self.ICON_SIZE_PX)
        self.copy_b.to_x(self.x + w - self.MARGIN_PX - self.ICON_SIZE_PX)
    
    def set_h(self, h):
        raise ValueError("このコンポーネントは高さを変更できない。")
    
    def set_colors(self, fill: int = COLOR_BLACK, background: int = COLOR_PRIMARY):
        self.background = background
        self.field.set_colors(text=fill, backgroud=background, border=background)
        self.copy_b.set_colors(text=fill, backgroud=background, border=background)
        self.to_x(self.x)
        self.to_y(self.y)
        self.set_w(self.w)

    def __hdl_copy(self):
        pyperclip.copy(self.text)

    def update(self):
        self.copy_b.update()
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, self.background)
        self.field.draw()
        self.copy_b.draw()
