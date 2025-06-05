from ...base.view import View, Area
from ..game_setting.multiplayer import MultiplayerGameSettingScene
from .lobby import Lobby
from ..player_type import PlayerType
from ...sequencer.access_key import AccessKeyManager
from ...areas.notice import FrontNotice
from ...sequencer.game_access import HostAccessSequencer, Error
from src.pyxres import *
from src.dialog.error import ErrorDialog

from typing import *
import tkinter as tk
from tkinter import messagebox

import pyxel 

class HostScene(View, Area):
    def __init__(self,
        x: float, y: float, w: float, h: float,
        on_cancel: Callable[[], None]
    ):
        self.init_area(x, y, w, h)
        
        # ホストゲームを離脱するコールバックイベント
        self.on_cancel = on_cancel
        
        # 状態表示
        self.notice = FrontNotice(x + w / 2 - 150, y + h / 2, 300, 50)
        
        self.akm: AccessKeyManager
        self.ak: str | None
        self.access_sequencer: HostAccessSequencer | None
        
        # 最初の画面を表示
        self.show_setting()
        
    def _hdl_accesskey_error(self):
        self.notice.put("FAILED TO GET ACCESS KEY", COLOR_FAILURE, 6000)
        
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを表示しない
        messagebox.showerror("Error", self.akm.error_message)
        root.destroy()
    
    def _hdl_get_accesskey(self, key: str):
        if len(key) < 512:
            self.notice.put("NO ACCESS KEY SET", COLOR_FAILURE, 6000)
            return
        self.ak = key
        
        if isinstance(self.scene, MultiplayerGameSettingScene):
            self.scene.allowed_to_access()
        else:
            raise ValueError("設定シーン以外でアクセスキー取得が完了した。")
        
        self.access_sequencer = HostAccessSequencer(self.ak, self._hdl_access_error)
    
    def _hdl_save_accesskey(self):
        raise RuntimeError("誤った実装によってアクセスキーを更新した。")
    
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

        self.show_setting()
        
    def _hdl_hosted_to_server(self, players_password: List[str]):
        if not isinstance(self.scene, MultiplayerGameSettingScene):
            raise ValueError("設定シーン以外でサーバ接続が完了した。")
        
        psp = players_password.copy()

        players_data_list: List[Tuple[str, PlayerType]] = []
        for player_type in self.scene.get_playsers():
            if player_type == PlayerType.MULTIPLAYER:
                if not players_password:
                    raise ValueError("画面とサーバレスポンスでユーザ数が異なる。")

                players_data_list.append( (psp.pop(), player_type) )
            else:
                players_data_list.append( ("", player_type) )

        self.show_lobby(players_data_list)
    
    def _hdl_player_joined(self, password: str):
        raise RuntimeError("Not implemented")
    
    def _hdl_all_players_here(self, ok: bool):
        raise RuntimeError("Not implemented")
    
    def show_setting(self):
        # アクセスキー管理
        self.akm = AccessKeyManager(self._hdl_accesskey_error, self._hdl_get_accesskey, self._hdl_save_accesskey)
        ok = self.akm.load()
        if not ok: raise RuntimeError("予期しないリソースの競合。")
        self.ak = None
        
        # 通信シーケンサー
        self.access_sequencer = None

        # シーンを設定
        self.scene: View = MultiplayerGameSettingScene(
            self.x, self.y, self.w, self.h,
            self.on_cancel,
            self._hdl_try_to_connect
        )
    
    def show_lobby(self, data: List[Tuple[str, PlayerType]]):
        self.scene = Lobby(self.x, self.y, self.w, self.h, self.show_setting, data)
    
    def _hdl_try_to_connect(self, player_number: int):
        if self.access_sequencer is None:
            raise ValueError("設定画面が許可されないタイミングで接続を要求した。")
        self.access_sequencer.connect(player_number, (
            self._hdl_hosted_to_server,
            self._hdl_player_joined,
            self._hdl_all_players_here
         ) )

    def update(self):
        self.akm.update()
        if self.access_sequencer is not None:
            self.access_sequencer.update()
            
        self.scene.update()
        self.notice.update()

    def draw(self):
        self.scene.draw()
        self.notice.draw()
