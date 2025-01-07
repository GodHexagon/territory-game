from ...base.view import View, Area
from ...areas.text import WritenText
from ..player_type import PlayerType
from ...areas.button import TextButton
from .components import Player, ProgressingIndicator, RadioButton
from src.pyxres import *

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
        super().init_area(x, y, w, h)

        self.on_launch_game = on_launch_game
        self.on_cancel = on_cancel
        self.multiplayer = multiplay

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
        self.start_button = TextButton(0, y + 96 + 48 * 4 + 32, label="GAME START", 
                                        on_click=self.__hdl_try_to_connect if multiplay else self.__hdl_launch_game)
        self.start_button.to_x_end(x + w - MARGIN)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
        
        # 戻るボタン
        self.cancel_button = TextButton(0, y + 96 + 48 * 4 + 32, label="CANCEL",
            on_click=lambda : self.on_cancel()
        )
        self.cancel_button.to_x(x + MARGIN)
        self.cancel_button.label.to_center_pos(*self.cancel_button.get_center_pos())

        # 処理中インジケータ
        self.prog = ProgressingIndicator(w / 2, y + 96 + 48 * 4 + 96, scale=5)
        
    def __hdl_try_to_connect(self):
        self.connecting = True

        self.prog.set_visible(True)

        self.start_button.change_mode("CANCEL CONNECTING", self.__hdl_cancel_connecting)
        self.start_button.to_x_end(self.x + self.w - GameSettingScene.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_cancel_connecting(self):
        self.connecting = False

        self.prog.set_visible(False)

        self.start_button.set_enabled(False)
        self.start_button.change_mode("GAME START", self.__hdl_try_to_connect)
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
        multiplayer_cound = 0
        for p in self.players:
            if p.type == PlayerType.PLAYABLE: playable_count += 1
            elif p.type == PlayerType.UNASSIGNED: unassigned_count += 1
            elif p.type == PlayerType.MULTIPLAYER: multiplayer_cound += 1
        self.start_button.set_enabled(
            playable_count == 1 and 
            unassigned_count in range(0, 3) and
            (not self.multiplayer or multiplayer_cound in range(1, 4))
        )
    
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
