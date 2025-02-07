from ..view import View, Area, CenteredArea
from ..limitter import LimitableArea
from ..areas.text import WritenText
from .player_type import PlayerType
from src.pyxres import COLOR_BLACK, COLOR_WHITE, COLOR_PRIMARY, COLOR_GRAY, BLUE_COLOR_S, RED_COLOR_S, GREEN_COLOR_S, YELLOW_COLOR_S

import pyxel

from typing import *

class GameSettingScene(Area, View):
    TEXT_COLOR = COLOR_BLACK
    BACKGROUND_COLOR = COLOR_WHITE

    COMUNM_NAMES_Y = 80
    LEFT_MARGIN_PX = 32
    PLAYABLE_CENTER_X = 192
    AI_CENTER_X = 256
    UNASSIGNED_CENTER_X = 320

    PLAYER_COLORS = (
        (0, BLUE_COLOR_S, "BLUE"),
        (1, RED_COLOR_S, "RED"),
        (2, GREEN_COLOR_S, "GREEN"),
        (3, YELLOW_COLOR_S, "YELLOW")
    )

    def __init__(self, x, y, w, h, on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None]):
        if not (x == 0 and y == 0): raise ValueError('このAreaは画面サイズ依存です。')
        super().__init__(x, y, w, h)

        self.on_launch_game = on_launch_game

        MARGIN = GameSettingScene.LEFT_MARGIN_PX

        self.title = WritenText(0, y + 32, "SETTING FOR PLAYING", GameSettingScene.TEXT_COLOR, 5)
        self.title.x = x + MARGIN

        PCX = self.PLAYABLE_CENTER_X
        ACX = self.AI_CENTER_X
        UCX = self.UNASSIGNED_CENTER_X
        Y = self.COMUNM_NAMES_Y
        self.column_names = (
            WritenText(0, y + Y, "NAME", GameSettingScene.TEXT_COLOR),
            WritenText(PCX, y + Y, "YOU", GameSettingScene.TEXT_COLOR),
            WritenText(ACX, y + Y, "AI", GameSettingScene.TEXT_COLOR),
            WritenText(UCX, y + Y, "NONE", GameSettingScene.TEXT_COLOR)
        )
        self.column_names[0].x = x + MARGIN

        PCS = GameSettingScene.PLAYER_COLORS

        l: List[Player] = []
        for i, color, color_name in PCS:
            callback = lambda type, i=i: self.__hdl_change_player_type(i, type)
            player = Player(
                x + MARGIN,
                y + i * 48 + 96,
                w - 64,
                color_name,
                color,
                callback,
                default=PlayerType.PLAYABLE if i == 0 else PlayerType.AI
            )
            l.append(player)
        self.players = l

        self.buttons = [p.ini_radios() for p in self.players]

        self.start_button = StartButton(0, y + 96 + 48 * 4 + 32, 
            lambda : self.on_launch_game(list(
                (pc[2], p.type) for pc, p in zip(PCS, self.players)
            ))
        )
        self.start_button.to_x_bottom(w - MARGIN)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_change_player_type(self, which: int, player_type: 'PlayerType'):
        self.players[which].set_player_type(player_type)

        playable_count = 0
        unassigned_count = 0
        for p in self.players:
            if p.type == PlayerType.PLAYABLE: playable_count += 1
            elif p.type == PlayerType.UNASSIGNED: unassigned_count += 1
        self.start_button.set_enabled(playable_count == 1 and unassigned_count in range(0, 3))
    
    def update(self):
        for rs in self.buttons:
            for r in rs:
                r.update()
        self.start_button.update()
    
    def draw(self):
        pyxel.cls(self.BACKGROUND_COLOR)
        self.title.draw()
        for c in self.column_names:
            c.draw()
        for p in self.players:
            p.draw()
        self.start_button.draw()

class StartButton(CenteredArea, LimitableArea):
    MARGIN_PX = 6
    
    def __init__(self, cx: float, cy: float, on_click: Callable[[], None]):
        self.on_click = on_click

        super().__init__(0, 0, 0, 0)
        self.write_label(cx, cy)

        self.set_limiteds()
    
    def write_label(self, cx: float, cy: float, color: int = COLOR_BLACK) -> None:
        self.label = WritenText(cx, cy, "GAME START", color)

        MARGIN = StartButton.MARGIN_PX
        self.w, self.h = (
            self.label.w + MARGIN * 2,
            self.label.h + MARGIN * 2
        )
        self.to_center_pos(cx, cy)
    
    def set_enabled(self, enabled: bool):
        self.write_label(
            *self.get_center_pos(),
            COLOR_BLACK if enabled else COLOR_GRAY
        )
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.on_click()

    def draw(self):
        self.drawer.rectb(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()

class Player(LimitableArea):
    HEIGHT_PX = 32

    def __init__(self, x, y, w, label: str, label_color: int, on_change: Callable[[PlayerType], None], default: PlayerType = PlayerType.AI):
        super().__init__(x, y, w, Player.HEIGHT_PX)
        self.set_limiteds()

        self.on_change = on_change
        self.type = default

        self.label = WritenText(0, y + self.h / 2, label, label_color, scale=3)
        self.label.x = x + 16
    
    def ini_radios(self) -> Tuple['RadioButton', ...]:
        self.buttons = (
            RadioButton(GameSettingScene.PLAYABLE_CENTER_X, self.y + self.h / 2, self.__hdl_click_playable, self.type == PlayerType.PLAYABLE),
            RadioButton(GameSettingScene.AI_CENTER_X, self.y + self.h / 2, self.__hdl_click_ai, self.type == PlayerType.AI),
            RadioButton(GameSettingScene.UNASSIGNED_CENTER_X, self.y + self.h / 2, self.__hdl_click_unassigned, self.type == PlayerType.UNASSIGNED)
        )
        return self.buttons
    
    def set_player_type(self, player_type: PlayerType):
        self.type = player_type
        self.buttons[0].set_selected(player_type == PlayerType.PLAYABLE)
        self.buttons[1].set_selected(player_type == PlayerType.AI)
        self.buttons[2].set_selected(player_type == PlayerType.UNASSIGNED)
    
    def __hdl_click_playable(self):
        self.on_change(PlayerType.PLAYABLE)
    
    def __hdl_click_ai(self):
        self.on_change(PlayerType.AI)
    
    def __hdl_click_unassigned(self):
        self.on_change(PlayerType.UNASSIGNED)
    
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
    
    def set_selected(self, selected: bool):
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
            self.drawer.circ(cx, cy, self.RADIUS_PX // 4, LINE)
