from .game_setting import GameSettingScene
from ..player_type import PlayerType
from ...sequencer.access_key import AccessKeyManager
from ...areas.notice import FrontNotice
from .components import Player, ProgressingIndicator, RadioButton, SceneData, ReadonlyText
from src.pyxres import *

from typing import *

class MultiplayerGameSettingScene(GameSettingScene):
    def __init__(self, 
        x: float, y: float, w: float, h: float,
        on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None], 
        on_cancel: Callable[[], None]
    ):
        self.init_scene(x, y, w, h, on_launch_game, on_cancel, multiplayer=True)

        for p in self.players[1:]:
            p.set_player_type(PlayerType.MULTIPLAYER)
        
        self.start_button.set_enabled(False)
        
        self.p_fields: List[ReadonlyText] | None = None

        self.notice = FrontNotice(x + w / 2 - 150, y + h / 2, 300, 50)
        
        self.akm = AccessKeyManager(self.__hdl_accesskey_error, self.__hdl_get_accesskey, self.__hdl_save_accesskey)
        ok = self.akm.load()
        if not ok: raise RuntimeError("予期しないリソースの競合。")
        self.ak: str | None = None
    
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
        
    def hdl_try_to_connect(self):
        self.freezed_setting = True

        self.prog.set_visible(True)

        self.start_button.change_mode("CANCEL CONNECTING", self.__hdl_cancel_connecting)
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
    
    def __hdl_cancel_connecting(self):
        self.prog.set_visible(False)

        self.start_button.set_enabled(False)
        self.start_button.change_mode("GAME START", self.hdl_try_to_connect)
        self.start_button.to_x_end(self.x + self.w - SceneData.LEFT_MARGIN_PX)
        self.start_button.label.to_center_pos(*self.start_button.get_center_pos())
        
    def __hdl_recieved_response(self):
        l: List[ReadonlyText] = []
        for p in self.players:
            if p.type != PlayerType.MULTIPLAYER: continue

            new = ReadonlyText(lambda _: None)
            new.to_center_pos(*p.get_center_pos())
            new.to_x(SceneData.PASSWORD_START_X)
            
            l.append(new)
        self.p_fields = l
        
    def update(self):
        if self.p_fields is not None:
            for f in self.p_fields:
                f.update()
        self.notice.update()
        self.akm.update()
        return super().update()

    def draw(self):
        super().draw()
        if self.p_fields is not None:
            for f in self.p_fields:
                f.draw()
        self.notice.draw()
