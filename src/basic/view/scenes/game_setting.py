from ..view import View, Area, CenteredArea
from ..limitter import LimitableArea
from ..areas.text import DrawnText
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
            self.y + i * 96,
            self.w - 64,
            f"player {i + 1}",
            lambda pt: ()
        ) for i in range(4)]

        self.radios = [p.ini_radios() for p in self.players]
    
    def update(self):
        for rs in self.radios:
            for r in rs:
                r.update()
    
    def draw(self):
        pyxel.cls(self.BACKGROUND_COLOR)
        for p in self.players:
            p.draw()
        for rs in self.radios:
            for r in rs:
                r.draw()
        
class PlayerType(Enum):
    AI = 0
    PLAYABLE = 1

class Player(LimitableArea):
    HEIGHT_PX = 64

    def __init__(self, x, y, w, label: str, on_change: Callable[[PlayerType] , None]):
        super().__init__(x, y, w, Player.HEIGHT_PX)
        self.set_limiteds()
        self.on_change = on_change

        self.label = DrawnText(x, y, label, GameSettingScene.TEXT_COLOR, 3)
    
    def ini_radios(self,) -> Tuple['RadioButton', 'RadioButton']:
        return (
            RadioButton(self.x + 32, self.y + 32, lambda: (
                self.on_change(PlayerType.PLAYABLE)
            )),
            RadioButton(self.x + 64, self.y + 32, lambda: self.on_change(PlayerType.AI))
        )
    
    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()
    

class RadioButton(CenteredArea, LimitableArea, View):
    SIZE_PX = 16

    def __init__(self, cx, cy, on_click: Callable[[], None]):
        super().__init__(0, 0, self.SIZE_PX, self.SIZE_PX)
        self.to_center_pos(cx, cy)
        self.set_limiteds()
        self.selected = False
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
        self.drawer.circ(cx, cy, self.SIZE_PX // 2, LINE)
        self.drawer.circb(cx, cy, self.SIZE_PX // 2, EMPTY)
        if self.selected:
            self.drawer.circ(cx, cy, self.SIZE_PX // 3, LINE)
