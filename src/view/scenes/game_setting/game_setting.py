from ...base.view import View, Area
from ...areas.text import WritenText
from ..player_type import PlayerType
from ...areas.button import TextButton
from .components import Player, ProgressingIndicator, RadioButton, SceneData
from src.pyxres import *

import pyxel

from typing import *
from abc import ABC, abstractmethod

class GameSettingScene(Area, View, ABC):
    def init_scene(self, x, y, w, h, 
            on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None], 
            on_cancel: Callable[[], None],
            multiplayer: bool = False
        ):
        if not (x == 0 and y == 0): raise ValueError('このAreaは画面サイズ依存です。')
        super().init_area(x, y, w, h)

        self.on_launch_game = on_launch_game
        self.on_cancel = on_cancel
        self.multiplayer = multiplayer

        # 画面タイトル
        MARGIN = SceneData.LEFT_MARGIN_PX

        self.title = WritenText(0, y + 32, "SETTING FOR PLAYING", SceneData.TEXT_COLOR, 5)
        self.title.x = x + MARGIN

        # 列名
        PCX = SceneData.PLAYABLE_CENTER_X
        ACX = SceneData.AI_CENTER_X
        UCX = SceneData.UNASSIGNED_CENTER_X
        MCX = SceneData.MULTIPLAY_CENTER_X
        Y = SceneData.COMUNM_NAMES_Y
        self.column_names: Tuple[WritenText, ...] = (
            WritenText(0, y + Y, "NAME", SceneData.TEXT_COLOR),
            WritenText(PCX, y + Y, "YOU", SceneData.TEXT_COLOR),
            WritenText(ACX, y + Y, "AI", SceneData.TEXT_COLOR),
            WritenText(UCX, y + Y, "NONE", SceneData.TEXT_COLOR)
        )
        if multiplayer: self.column_names += (WritenText(MCX, y + Y, "ONLINE", SceneData.TEXT_COLOR), )

        self.column_names[0].x = x + MARGIN

        # プレイヤー表（行）
        PCS = SceneData.PLAYER_COLORS

        l: List[Player] = []
        for i, color, color_name in PCS:
            callback = lambda type, i=i: self.hdl_change_player_type(i, type)
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

        self.buttons = [p.ini_radios(multiplay=multiplayer) for p in self.players]

        # スタートボタン
        self.connecting = False
        self.start_button = TextButton(0, y + 96 + 48 * 4 + 32, label="GAME START", 
                                        on_click=self.__hdl_try_to_connect if multiplayer else self.__hdl_launch_game)
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
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_cancel_connecting(self):
        self.connecting = False

        self.prog.set_visible(False)

        self.start_button.set_enabled(False)
        self.start_button.change_mode("GAME START", self.__hdl_try_to_connect)
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_launch_game(self):
        PCS = SceneData.PLAYER_COLORS
        self.on_launch_game(list(
            (pc[2], p.type) for pc, p in zip(PCS, self.players)
        ))
    
    @abstractmethod
    def hdl_change_player_type(self, which: int, player_type: 'PlayerType'):
        pass
    
    def update(self):
        if not self.connecting:
            for rs in self.buttons:
                for r in rs:
                    r.update()
        self.start_button.update()
        self.cancel_button.update()
        self.prog.update()
    
    def draw(self):
        pyxel.cls(SceneData.BACKGROUND_COLOR)
        self.title.draw()
        for c in self.column_names:
            c.draw()
        for p in self.players:
            p.draw()
        for rs in self.buttons:
            for r in rs:
                r.draw()
        self.start_button.draw()
        self.cancel_button.draw()
        self.prog.draw()

class SingleplayerGameSettingScene(GameSettingScene):
    def __init__(self, 
        x: float, y: float, w: float, h: float,
        on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None], 
        on_cancel: Callable[[], None]
    ):
        self.init_scene(x, y, w, h, on_launch_game, on_cancel, multiplayer=False)

    def hdl_change_player_type(self, which, player_type):
        self.players[which].set_player_type(player_type)

        playable_count = 0
        unassigned_count = 0
        for p in self.players:
            if p.type == PlayerType.PLAYABLE: playable_count += 1
            elif p.type == PlayerType.UNASSIGNED: unassigned_count += 1
        self.start_button.set_enabled(
            playable_count == 1 and 
            unassigned_count in range(0, 3)
        )

class MultiplayerGameSettingScene(GameSettingScene):
    def __init__(self, 
        x: float, y: float, w: float, h: float,
        on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None], 
        on_cancel: Callable[[], None]
    ):
        self.init_scene(x, y, w, h, on_launch_game, on_cancel, multiplayer=True)
        for p in self.players[1:]:
            p.set_player_type(PlayerType.MULTIPLAYER)
    
    def hdl_change_player_type(self, which, player_type):
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
            multiplayer_cound in range(1, 4)
        )
