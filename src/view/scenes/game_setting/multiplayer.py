from .game_setting import GameSettingScene
from ..player_type import PlayerType
from ...sequencer.access_key import AccessKeyManager
from ...sequencer.game_access import HostAccessSequencer, Error
from .components import SceneData, ReadonlyText
from src.pyxres import *

from typing import *

import pyxel

class MultiplayerGameSettingScene(GameSettingScene):
    def __init__(self, 
        x: float, y: float, w: float, h: float,
        on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None], 
        on_cancel: Callable[[], None]
    ):
        self.init_scene(x, y, w, h, on_launch_game, on_cancel, multiplayer=True)

        # キャンセル状態
        self.cancel_flag = False

        # 連打禁止
        self.restriction_end_frame = 0

        # ラジオボタンの初期値設定
        for p in self.players[1:]:
            p.set_player_type(PlayerType.MULTIPLAYER)
        
        # アクセスキーが取得できるまで禁止
        self.start_button.set_enabled(False)
        
        # パスワードテキストフィールド
        self.p_fields: List[ReadonlyText] | None = None

        
        # アクセスキー管理
        self.akm = AccessKeyManager(self.__hdl_accesskey_error, self.__hdl_get_accesskey, self.__hdl_save_accesskey)
        ok = self.akm.load()
        if not ok: raise RuntimeError("予期しないリソースの競合。")
        self.ak: str | None = None

        # 通信シーケンサー
        self.access_sequencer: HostAccessSequencer | None = None
        self.player_number = 4
    
    def __hdl_accesskey_error(self):
        self.notice.put("FAILED TO GET ACCESS KEY", COLOR_FAILURE, 6000)
    
    def __hdl_get_accesskey(self, key: str):
        if len(key) < 512:
            self.notice.put("NO ACCESS KEY SET", COLOR_FAILURE, 6000)
            return
        self.ak = key
        self.start_button.set_enabled(True)
    
    def __hdl_save_accesskey(self):
        raise RuntimeError("誤ってアクセスキーを更新した。")
    
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
            multiplayer_cound in range(1, 4) and
            self.ak is not None
        )

        self.player_number = playable_count + multiplayer_cound
        
    def hdl_try_to_connect(self):
        self.prog.set_visible(True)

        self.connecting = True

        self.start_button.change_mode("CANCEL CONNECTING", self.__hdl_cancel_connecting)
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())

        if self.ak is None: raise RuntimeError("アクセスキーを取得する前に接続を試みようとした。")

        self.access_sequencer = HostAccessSequencer(self.ak, self.__hdl_access_error)
        self.access_sequencer.connect(self.player_number, (
            self.__hdl_hosted_to_server,
            self.__hdl_player_joined,
            self.__hdl_all_players_here
         ) )
    
    def __hdl_cancel_connecting(self):
        self.prog.set_visible(False)

        self.start_button.set_enabled(False)
        self.start_button.change_mode("GAME START", self.hdl_try_to_connect)
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())

        self.cancel_flag = True
        
    def __hdl_hosted_to_server(self, players_password: List[str]):
        if self.cancel_flag:
            self.restriction_end_frame = pyxel.frame_count + 30
        else:
            self.on_launch_game([
                .
            ])
    
    def __hdl_player_joined(self, password: str):
        raise RuntimeError("not implement")
    
    def __hdl_all_players_here(self, ok: bool):
        raise RuntimeError("not implement")
        
    def update(self):
        if self.restriction_end_frame == pyxel.frame_count:
            self.start_button.set_enabled(True)
            self.connecting = False

        if self.p_fields is not None:
            for f in self.p_fields:
                f.update()
        self.notice.update()
        
        self.akm.update()

        if self.access_sequencer is not None:
            self.access_sequencer.update()

        return super().update()

    def draw(self):
        super().draw()

        if self.p_fields is not None:
            for f in self.p_fields:
                f.draw()
        self.notice.draw()
