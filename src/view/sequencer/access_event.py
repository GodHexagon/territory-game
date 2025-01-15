from abc import ABC, abstractmethod
from typing import *
from threading import Lock
from enum import Enum

from ..base.view import View

_T = TypeVar("_T")

class SequencerEvent(View, Generic[_T]):
    def __init__(self, on_complete: Callable[[_T], None]):
        list
        self._on_complete = on_complete
        self._lock = Lock()
        self._lock.acquire()
        self._arg: _T | None = None

    def pend(self, arg: _T):
        if not self._lock.locked(): ValueError("コールバックが実行される前に新しいイベントを追加しようとている。")
        if arg is None: ValueError("引数Noneは非対応。")
        self._arg = arg
        self._lock.release()

    def update(self):
        if self._lock.acquire(blocking=False) and self._arg is not None:
            self._on_complete(self._arg)
            self._arg = None
    
    def draw(self):
        pass
