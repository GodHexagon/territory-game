from ...view import View, Area, CenteredArea
from ...limitter import LimitableArea
from ...areas.text import WritenText
from ..player_type import PlayerType
from src.pyxres import COLOR_BLACK, COLOR_WHITE, COLOR_PRIMARY, COLOR_GRAY, BLUE_COLOR_S, RED_COLOR_S, GREEN_COLOR_S, YELLOW_COLOR_S, COLOR_FAILURE

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
    MULTIPLAY_CENTER_X = 400

    PLAYER_COLORS = (
        (0, BLUE_COLOR_S, "BLUE"),
        (1, RED_COLOR_S, "RED"),
        (2, GREEN_COLOR_S, "GREEN"),
        (3, YELLOW_COLOR_S, "YELLOW")
    )

    def __init__(self, x, y, w, h, 
            on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None], 
            on_cancel: Callable[[], None],
            multiplay: bool = False
        ):
        if not (x == 0 and y == 0): raise ValueError('このAreaは画面サイズ依存です。')
        super().__init__(x, y, w, h)

        self.on_launch_game = on_launch_game
        self.on_cancel = on_cancel
        self.multiplay = multiplay

        # 画面タイトル
        MARGIN = GameSettingScene.LEFT_MARGIN_PX

        self.title = WritenText(0, y + 32, "SETTING FOR PLAYING", GameSettingScene.TEXT_COLOR, 5)
        self.title.x = x + MARGIN

        # 列名
        PCX = self.PLAYABLE_CENTER_X
        ACX = self.AI_CENTER_X
        UCX = self.UNASSIGNED_CENTER_X
        MCX = self.MULTIPLAY_CENTER_X
        Y = self.COMUNM_NAMES_Y
        self.column_names: Tuple[WritenText, ...] = (
            WritenText(0, y + Y, "NAME", GameSettingScene.TEXT_COLOR),
            WritenText(PCX, y + Y, "YOU", GameSettingScene.TEXT_COLOR),
            WritenText(ACX, y + Y, "AI", GameSettingScene.TEXT_COLOR),
            WritenText(UCX, y + Y, "NONE", GameSettingScene.TEXT_COLOR)
        )
        if multiplay: self.column_names += (WritenText(MCX, y + Y, "ONLINE", GameSettingScene.TEXT_COLOR), )

        self.column_names[0].x = x + MARGIN

        # プレイヤー表（行）
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

        self.buttons = [p.ini_radios(multiplay=multiplay) for p in self.players]

        # スタートボタン
        self.connecting = False
        self.start_button = StartButton(0, y + 96 + 48 * 4 + 32, "GAME START", 
                                        self.__hdl_try_to_connect if multiplay else self.__hdl_launch_game)
        self.start_button.to_x_end(x + w - MARGIN)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
        
        # 戻るボタン
        self.cancel_button = StartButton(0, y + 96 + 48 * 4 + 32, "CANCEL",
            lambda : self.on_cancel()
        )
        self.cancel_button.to_x(x + MARGIN)
        self.cancel_button.label.to_center_pos(*self.cancel_button.get_center_pos())

        # 処理中インジケータ
        self.prog = ProgressingIndicator(w / 2, y + 96 + 48 * 4 + 96, scale=5)
        
    def __hdl_try_to_connect(self):
        self.connecting = True

        self.prog.set_visible(True)

        self.start_button.chage_mode("CANCEL CONNECTING", self.__hdl_cancel_connecting)
        self.start_button.to_x_end(self.x + self.w - GameSettingScene.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_cancel_connecting(self):
        self.connecting = False

        self.prog.set_visible(False)

        self.start_button.set_enabled(False)
        self.start_button.chage_mode("GAME START", self.__hdl_try_to_connect)
        self.start_button.to_x_end(self.x + self.w - GameSettingScene.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_launch_game(self):
        PCS = GameSettingScene.PLAYER_COLORS
        self.on_launch_game(list(
            (pc[2], p.type) for pc, p in zip(PCS, self.players)
        ))
    
    def __hdl_change_player_type(self, which: int, player_type: 'PlayerType'):
        self.players[which].set_player_type(player_type)

        playable_count = 0
        unassigned_count = 0
        for p in self.players:
            if p.type == PlayerType.PLAYABLE: playable_count += 1
            elif p.type == PlayerType.UNASSIGNED: unassigned_count += 1
        self.start_button.set_enabled(playable_count == 1 and unassigned_count in range(0, 3))
    
    def update(self):
        if not self.connecting:
            for rs in self.buttons:
                for r in rs:
                    r.update()
        self.start_button.update()
        self.cancel_button.update()
        self.prog.update()
    
    def draw(self):
        pyxel.cls(self.BACKGROUND_COLOR)
        self.title.draw()
        for c in self.column_names:
            c.draw()
        for p in self.players:
            p.draw()
        self.start_button.draw()
        self.cancel_button.draw()
        self.prog.draw()

class ProgressingIndicator(WritenText):
    def __init__(self, cx, cy, scale = 3, parent_surface = None, visible: bool = False):
        super().__init__(cx, cy, "Connecting to server.", COLOR_FAILURE, scale, parent_surface)
        self.animation_sequence = 0
        self.set_visible(visible)
    
    def update(self):
        new_seq = (pyxel.frame_count // 30) % 3
        if self.animation_sequence != new_seq:
            self.rewrite("Connecting to server" + "."*(new_seq + 1), COLOR_FAILURE)
            self.animation_sequence = new_seq
    
    def set_visible(self, visible: bool):
        self.visible = visible
    
    def draw(self):
        if self.visible: super().draw()

class StartButton(CenteredArea, LimitableArea):
    MARGIN_PX = 6
    
    def __init__(self, cx: float, cy: float, label: str, on_click: Callable[[], None]):
        self.text = label
        self.on_click = on_click

        self.enabled = True

        super().__init__(0, 0, 0, 0)
        self.__write_label(cx, cy)

        self.set_limiteds()
    
    def chage_mode(self, label: str, on_click: Callable[[], None]):
        self.text = label
        self.on_click = on_click
        
        self.__write_label(*self.get_center_pos())
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        self.__write_label(
            *self.get_center_pos()
        )
        
    def __write_label(self, cx: float, cy: float) -> None:
        self.label = WritenText(cx, cy, self.text, COLOR_BLACK if self.enabled else COLOR_GRAY)

        MARGIN = StartButton.MARGIN_PX
        self.w, self.h = (
            self.label.w + MARGIN * 2,
            self.label.h + MARGIN * 2
        )
        self.to_center_pos(cx, cy)
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.enabled:
            self.on_click()

    def draw(self):
        self.drawer.rectb(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()

class Player(LimitableArea):
    HEIGHT_PX = 32

    def __init__(self, x, y, w, 
            label: str, 
            label_color: int, 
            on_change: Callable[[PlayerType], None], 
            default: PlayerType = PlayerType.AI
        ):
        super().__init__(x, y, w, Player.HEIGHT_PX)
        self.set_limiteds()

        self.on_change = on_change
        self.type = default

        self.label = WritenText(0, y + self.h / 2, label, label_color, scale=3)
        self.label.x = x + 16
    
    def ini_radios(self, multiplay: bool = False) -> Tuple['RadioButton', ...]:
        PCX = GameSettingScene.PLAYABLE_CENTER_X
        ACX = GameSettingScene.AI_CENTER_X
        UCX = GameSettingScene.UNASSIGNED_CENTER_X
        MCX = GameSettingScene.MULTIPLAY_CENTER_X
        Y = self.y + self.h / 2
        self.buttons: Tuple[RadioButton, ...] = (
            RadioButton(PCX, Y, self.__hdl_click_playable, self.type == PlayerType.PLAYABLE),
            RadioButton(ACX, Y, self.__hdl_click_ai, self.type == PlayerType.AI),
            RadioButton(UCX, Y, self.__hdl_click_unassigned, self.type == PlayerType.UNASSIGNED)
        )
        if multiplay: self.buttons += (RadioButton(MCX, Y, self.__hdl_click_multiplayer, self.type == PlayerType.MULTIPLAYER), )

        return self.buttons
    
    def set_player_type(self, player_type: PlayerType):
        self.type = player_type
        ASSIGNMENT = (PlayerType.PLAYABLE, PlayerType.AI, PlayerType.UNASSIGNED, PlayerType.MULTIPLAYER)
        for i, b in enumerate(self.buttons):
            b.set_selected(player_type == ASSIGNMENT[i])
    
    def __hdl_click_playable(self):
        self.on_change(PlayerType.PLAYABLE)
    
    def __hdl_click_ai(self):
        self.on_change(PlayerType.AI)
    
    def __hdl_click_unassigned(self):
        self.on_change(PlayerType.UNASSIGNED)
    
    def __hdl_click_multiplayer(self):
        self.on_change(PlayerType.MULTIPLAYER)
    
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
