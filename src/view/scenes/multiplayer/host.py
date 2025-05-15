from ...base.view import View, Area
from ..game_setting.multiplayer import MultiplayerGameSettingScene
from ...sequencer.game_access import HostAccessSequencer, Error
from .lobby import Lobby
from ..player_type import PlayerType
from ...areas.notice import FrontNotice
from src.pyxres import *
from src.dialog.error import ErrorDialog

from typing import *

import pyxel

class HostScene(View, Area):
    def __init__(self,
        x: float, y: float, w: float, h: float,
        on_cancel: Callable[[], None]
    ):
        self.init_area(x, y, w, h)

        self.on_cancel = on_cancel
        
        self.ak: str | None = None
        self.access_sequencer: HostAccessSequencer | None = None
        
        # 状態表示
        self.notice = FrontNotice(x + w / 2 - 150, y + h / 2, 300, 50)
        
        self.show_setting()
    
    def show_setting(self):
        self.scene: View = MultiplayerGameSettingScene(
            self.x, self.y, self.w, self.h,
            self.show_lobby,
            self.on_cancel
        )
    
    def show_lobby(self, data: List[Tuple[str, PlayerType]]):
        self.scene = Lobby(self.x, self.y, self.w, self.h, self.show_setting, data)

    def _hdl_get_access_key(self, ak: str):
        self.ak = ak
        self.access_sequencer = HostAccessSequencer(ak, self._hdl_access_error)
        
        return self.access_sequencer
        
    def _hdl_access_error(self, e: Error):
        if e == Error.IMPLEMENTATION_ERROR: raise ValueError("通信中の予期しないエラー。")
        elif e == Error.NETWORK_ERROR: self.notice.put("NETWORK ERROR", COLOR_FAILURE)
        elif e == Error.PUSHER_ERROR: self.notice.put("SERVER ERROR", COLOR_FAILURE)
        elif e == Error.SERVER_ERROR: self.notice.put("SERVER ERROR", COLOR_FAILURE)

        user_message = {
            Error.IMPLEMENTATION_ERROR : "IMPLEMENTATION_ERROR: 予期しないエラーが発生しました。よろしければ開発者に報告をお願いします。",
            Error.NETWORK_ERROR : "NETWORK_ERROR: ネットワークに接続できませんでした。お使いのネットワークを確認してください。",
            Error.PUSHER_ERROR : "PUSHER_ERROR: サーバに問題が発生しました。しばらく待ってからお試しください。",
            Error.SERVER_ERROR : "SERVER_ERROR: サーバに問題が発生しました。しばらく待ってからお試しください。",
        }
        ErrorDialog(user_message[e])

    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
