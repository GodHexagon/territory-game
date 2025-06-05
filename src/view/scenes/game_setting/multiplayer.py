from .game_setting import GameSettingScene
from ..player_type import PlayerType
from ...sequencer.game_access import HostAccessSequencer
from ...areas.notice import FrontNotice
from .components import SceneData, ReadonlyText
from src.pyxres import *

from typing import *

class MultiplayerGameSettingScene(GameSettingScene):
    def __init__(self, 
        x: float, y: float, w: float, h: float,
        on_cancel: Callable[[], None],
        on_try_to_connect: Callable[[int], None]
    ):
        self.init_scene(x, y, w, h, lambda x: None, on_cancel, multiplayer=True)

        self.on_try_to_connect = on_try_to_connect

        # ラジオボタンの初期値設定
        for p in self.players[1:]:
            p.set_player_type(PlayerType.MULTIPLAYER)
        self.player_number = 4
        
        # アクセスキーが取得できるまで禁止
        self.is_allow_to_access = False
        self.start_button.set_enabled(False)

        # 状態表示
        self.notice = FrontNotice(x + w / 2 - 150, y + h / 2, 300, 50)
    
    def allowed_to_access(self):
        self.is_allow_to_access = True
        self.start_button.set_enabled(True)

    def get_playsers(self) -> List[PlayerType]:
        return [p.type for p in self.players]
    
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
            self.is_allow_to_access
        )

        self.player_number = playable_count + multiplayer_cound
        
    def hdl_try_to_connect(self):
        self.prog.set_visible(True)

        self.connecting = True

        self.start_button.set_enabled(False)

        self.on_try_to_connect(self.player_number)
        
    def update(self):
        self.notice.update()
        return super().update()

    def draw(self):
        super().draw()
        self.notice.draw()
