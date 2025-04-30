from .game_setting import GameSettingScene
from ..player_type import PlayerType
from ...sequencer.access_key import AccessKeyManager
from ...sequencer.game_access import HostAccessSequencer, Error
from ...areas.notice import FrontNotice
from .components import SceneData, ReadonlyText
from src.pyxres import *
from src.dialog.error import ErrorDialog

from typing import *

class MultiplayerGameSettingScene(GameSettingScene):
    def __init__(self, 
        x: float, y: float, w: float, h: float,
        on_launch_game: Callable[[List[Tuple[str, PlayerType]]], None], 
        on_cancel: Callable[[], None]
    ):
        self.init_scene(x, y, w, h, on_launch_game, on_cancel, multiplayer=True)

        # ラジオボタンの初期値設定
        for p in self.players[1:]:
            p.set_player_type(PlayerType.MULTIPLAYER)
        
        # アクセスキーが取得できるまで禁止
        self.start_button.set_enabled(False)
        
        # 多分パスワードテキストフィールド
        self.p_fields: List[ReadonlyText] | None = None

        # 状態表示
        self.notice = FrontNotice(x + w / 2 - 150, y + h / 2, 300, 50)
        
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
    
    def __hdl_access_error(self, e: Error):
        user_message = {
            Error.IMPLEMENTATION_ERROR : "IMPLEMENTATION_ERROR: 予期しないエラーが発生しました。よろしければ開発者に報告をお願いします。",
            Error.NETWORK_ERROR : "NETWORK_ERROR: ネットワークに接続できませんでした。お使いのネットワークを確認してください。",
            Error.PUSHER_ERROR : "PUSHER_ERROR: サーバに問題が発生しました。しばらく待ってからお試しください。",
            Error.SERVER_ERROR : "SERVER_ERROR: サーバに問題が発生しました。しばらく待ってからお試しください。",
        }

        if e == Error.IMPLEMENTATION_ERROR: raise ValueError("通信中の予期しないエラー。")
        elif e == Error.NETWORK_ERROR: self.notice.put("NETWORK ERROR", COLOR_FAILURE)
        elif e == Error.PUSHER_ERROR: self.notice.put("SERVER ERROR", COLOR_FAILURE)
        elif e == Error.SERVER_ERROR: self.notice.put("SERVER ERROR", COLOR_FAILURE)

        ErrorDialog(user_message[e])
        
    def __hdl_hosted_to_server(self, players_password: List[str]):
        l: List[ReadonlyText] = []
        for p, password in zip(self.players, players_password):
            if p.type != PlayerType.MULTIPLAYER: continue

            new = ReadonlyText(lambda _: None, password)
            new.to_center_pos(*p.get_center_pos())
            new.to_x(SceneData.PASSWORD_START_X)
            
            l.append(new)
        self.p_fields = l
    
    def __hdl_player_joined(self, password: str):
        raise RuntimeError("not implement")
    
    def __hdl_all_players_here(self, ok: bool):
        raise RuntimeError("not implement")
        
    def update(self):
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
