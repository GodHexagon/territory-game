from .game_setting import GameSettingScene
from ..player_type import PlayerType
from ...sequencer.access_key import AccessKeyManager
from ...areas.notice import FrontNotice
from .components import Player, ProgressingIndicator, RadioButton, SceneData, ReadonlyText
from ...sequencer.game_access import HostAccessSequencer
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
        
        self.time_allow_connection = -1

        for p in self.players[1:]:
            p.set_player_type(PlayerType.MULTIPLAYER)
        
        self.start_button.set_enabled(False)
        
        self.p_fields: List[ReadonlyText] | None = None
        
        # 処理中インジケータ
        RH = SceneData.ROW_HEIGHT_PX
        RG = SceneData.ROW_GAP_PX
        self.prog = ProgressingIndicator(w / 2, y + 96 + (RH + RG) * 4 + 96, scale=5)

        self.notice = FrontNotice(x + w / 2 - 150, y + h / 2, 300, 50)
        
        self.akm = AccessKeyManager(self.__hdl_accesskey_error, self.__hdl_get_accesskey, self.__hdl_save_accesskey)
        ok = self.akm.load()
        if not ok: raise RuntimeError("予期しないリソースの競合。")

        self.access: HostAccessSequencer | None = None
    
    def __hdl_connection_error(self):
        self.notice.put("FAILED TO SERVER COMMUNICATION", COLOR_FAILURE, 6000)
        self.freezed_setting = True
        self.time_allow_connection = -1
        self.prog.set_visible(False)

    def __hdl_connected(self):
        self.on_launch_game()
    
    def __hdl_accesskey_error(self):
        self.notice.put("FAILED TO GET ACCESS KEY", COLOR_FAILURE, 6000)
    
    def __hdl_get_accesskey(self, key: str):
        if len(key) < 512:
            self.notice.put("NO ACCESS KEY SET", COLOR_FAILURE, 6000)
            return

        self.access = HostAccessSequencer(key, self.__hdl_connection_error)

        for p, i in zip(self.players, range(len(self.players))):
            self.hdl_change_player_type(i, p.type)
    
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
            self.access is not None
        )
        
    def hdl_try_to_connect(self):
        self.freezed_setting = True

        self.prog.set_visible(True)

        self.start_button.change_mode("CANCEL CONNECTING", self.__hdl_cancel_connecting)
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_cancel_connecting(self):
        self.time_allow_connection = pyxel.frame_count + 60

        self.prog.set_visible(False)

        self.access = HostAccessSequencer(self.access.commander.access_key, self.__hdl_connection_error)
        self.start_button.set_enabled(False)

        self.start_button.change_mode("GAME START", self.hdl_try_to_connect)
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def update(self):
        if self.freezed_setting and self.time_allow_connection != -1 and pyxel.frame_count >= self.time_allow_connection:
            self.freezed_setting = False
        
        if self.p_fields is not None:
            for f in self.p_fields:
                f.update()
        self.prog.update()
        self.notice.update()
        self.akm.update()
        self.access.update()
        return super().update()

    def draw(self):
        super().draw()
        if self.p_fields is not None:
            for f in self.p_fields:
                f.draw()
        self.prog.draw()
        self.notice.draw()
