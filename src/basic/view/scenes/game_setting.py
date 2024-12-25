from ..view import View, Area, CenteredArea
from ..limitter import LimitableArea
from ..areas.text import WritenText
from pyxres import COLOR_BLACK, COLOR_WHITE, COLOR_PRIMARY

import pyxel

from typing import *
from enum import Enum

class GameSettingScene(Area, View):
    TEXT_COLOR = COLOR_BLACK
    BACKGROUND_COLOR = COLOR_WHITE

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        self.players = [Player(
            self.x + 32,
            self.y + i * 48 + 32,
            self.w - 64,
            f"player {i + 1}",
            lambda _: None,
            PlayerType.PLAYABLE if i == 0 else PlayerType.AI
        ) for i in range(4)]

        self.buttons = [p.ini_radios() for p in self.players]
    
    def update(self):
        for rs in self.buttons:
            for r in rs:
                r.update()
    
    def draw(self):
        pyxel.cls(self.BACKGROUND_COLOR)
        for p in self.players:
            p.draw()
        
class PlayerType(Enum):
    PLAYABLE = 0
    AI = 1

class Player(LimitableArea):
    HEIGHT_PX = 32

    def __init__(self, x, y, w, label: str, on_change: Callable[[PlayerType], None], default: PlayerType = PlayerType.AI):
        super().__init__(x, y, w, Player.HEIGHT_PX)
        self.set_limiteds()

        self.on_change = on_change
        self.type = default

        self.label = WritenText(x + 128, y + self.h / 2, label, GameSettingScene.TEXT_COLOR, 3)
    
    def ini_radios(self) -> Tuple['RadioButton', 'RadioButton']:
        self.buttons = (
            RadioButton(self.x + self.w - 192, self.y + self.h / 2, self.__hdl_click_playable, self.type == PlayerType.PLAYABLE),
            RadioButton(self.x + self.w - 128, self.y + self.h / 2, self.__hdl_click_ai, self.type == PlayerType.AI)
        )
        return self.buttons
    
    def __hdl_click_playable(self):
        self.type = PlayerType.PLAYABLE
        self.buttons[0].change_selected(True)
        self.buttons[1].change_selected(False)
        self.on_change(self.type)
    
    def __hdl_click_ai(self):
        self.type = PlayerType.AI
        self.buttons[0].change_selected(False)
        self.buttons[1].change_selected(True)
        self.on_change(self.type)
    
    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()
        for b in self.buttons:
            b.draw()
    

class RadioButton(CenteredArea, LimitableArea, View):
    RADIUS_PX = 16

    def __init__(self, cx, cy, on_click: Callable[[], None], default: bool = False):
        super().__init__(0, 0, self.RADIUS_PX, self.RADIUS_PX)
        self.to_center_pos(cx, cy)
        self.set_limiteds()
        self.selected = default
        self.on_click = on_click
    
    def change_selected(self, selected: bool):
        self.selected = selected
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.on_click()
    
    def draw(self):
        LINE = GameSettingScene.TEXT_COLOR
        EMPTY = GameSettingScene.BACKGROUND_COLOR
        cx, cy = self.get_center_pos()
        self.drawer.circ(cx, cy, self.RADIUS_PX // 2, EMPTY)
        self.drawer.circb(cx, cy, self.RADIUS_PX // 2, LINE)
        if self.selected:
            self.drawer.circ(cx, cy, self.RADIUS_PX // 3, LINE)
