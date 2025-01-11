from ..base.view import View
from .queue_helper import TypedQueue
from ...access.commander import Commander

from typing import *
from enum import Enum

class GameAccessSequencer(View):
    def init_view(self,
        on_error_throwed: Callable[['Error'], None]
    ):
        pass

class HostAccessSequencer(GameAccessSequencer):
    def __init__(self,
        access_key: str,
        on_error_throwed: Callable[['Error'], None]
    ):
        self.commander = Commander(

        )

        self.on_error_throwed = on_error_throwed
        self.on_connected: Callable[[List[str]], None] | None = None

        self.cri_error_throwed: TypedQueue['Error'] = TypedQueue(maxsize=1)
        self.cri_connected: TypedQueue[List[str]] = TypedQueue(maxsize=1)
    
    def connect(self,
        on_connected: Callable[[List[str]], None]
    ):
        self.on_connected = on_connected
        

class Error(Enum):
    NETWORK_ERROR = 0
    IMPLEMENTATION_ERROR = 1
    SERVER_ERROR = 2
    PUSHER_ERROR = 3
