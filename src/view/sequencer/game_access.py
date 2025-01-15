from dataclasses import dataclass
from enum import Enum
from typing import *
from abc import ABC
from threading import Thread, Lock
import requests

from ...access.commander import Commander, PusherError
from .access_event import SequencerEvent
from ..base.view import View

class Error(Enum):
    NETWORK_ERROR = 0
    IMPLEMENTATION_ERROR = 1
    SERVER_ERROR = 2
    PUSHER_ERROR = 3

class EventsBundle(View):
    def __init__(self):
        self.lock = Lock()
        self.hosting_events = None
        
    HostCT: TypeAlias = Tuple[Callable[[List[str]], None], Callable[[str], None], Callable[[bool], None]]
    class HostIndex:
        ERROR_THROWED = 0
        HOST_TO_SERVER = 1
        PLAYER_JOINED = 2
    
    def change_to_host_connection(self, handlers: "EventsBundle.HostCT"):
        if self.lock.acquire(blocking=False):
            h = handlers[1]
            self.hosting_events = tuple(SequencerEvent(h) for h in handlers)
            self.lock.release()
        else:
            raise ValueError("イベント実行中は新しいモードに切り替えられない。")
    
    def get_host_connection_events(self):
        with self.lock:
            return self.hosting_events
    
    def update(self):
        if self.lock.acquire(blocking=False):
            events = self.hosting_events if self.hosting_events is not None else tuple()
            for e in events:
                e.update()
            self.lock.release()
    
    def draw(self):
        pass

class GameAccessSequencer(View, ABC):
    def init_view(self,
        on_error_throwed: Callable[['Error'], None]
    ):
        pass

    def update(self):
        pass
    
    def draw(self) -> None:
        """描画処理"""
        pass

class HostAccessSequencer(GameAccessSequencer):
    def __init__(self, access_key: str, on_error_throwed: Callable[[Error], None]):
        self.error_event = SequencerEvent(on_error_throwed)
        self._events = EventsBundle()

        self._commander = Commander(
            access_key,
            self._handle_error,
            lambda: None,
            self._handle_response,
            self._handle_game_message
        )

    def connect(self,
            player_number: int,
            handlers: EventsBundle.HostCT
        ) -> None:
        """
        handlers = tuple(on_hosted_to_server, on_player_joined, on_all_players_here)
        """
        self._events.change_to_host_connection(handlers)
        self._commander.host(player_number)

    def _handle_error(self, e: Exception) -> None:
        """エラーコールバック"""
        if isinstance(e, PusherError): self.error_event.pend(Error.PUSHER_ERROR)
        elif isinstance(e, OSError): self.error_event.pend(Error.NETWORK_ERROR)
        else: self.error_event.pend(Error.IMPLEMENTATION_ERROR)

    def _handle_response(self, response: requests.Response) -> None:
        """APIサーバ接続のレスポンスコールバック"""
        if 500 <= response.status_code and response.status_code <= 599: self.error_event.pend(Error.SERVER_ERROR)
        elif response.status_code == 408: self.error_event.pend(Error.NETWORK_ERROR)
        elif response.status_code != 200: self.error_event.pend(Error.IMPLEMENTATION_ERROR)
        
        evs = self._events.get_host_connection_events()
        ev = cast(SequencerEvent[str], evs[1])

    def _handle_game_message(self, message: str) -> None:
        """ゲームメッセージコールバック"""
        pass

    def update(self) -> bool:
        """
        フレームごとの更新処理
        """
        self._events.update()
        return super().update()
