from queue import Queue
from typing import TypeVar, Generic
T = TypeVar('T')  # 汎用型

class TypedQueue(Generic[T], Queue):
    def __init__(self, maxsize: int = 0):
        super().__init__(maxsize=maxsize)
        self._queue: list[T] = []  # 型アノテーション付きの内部リスト
    
    def put(self, item: T, block: bool = True, timeout: float | None = None) -> None:
        """型安全な要素の追加"""
        super().put(item, block=block, timeout=timeout)
    
    def get(self, block: bool = True, timeout: float | None = None) -> T:
        """型安全な要素の取得"""
        return super().get(block=block, timeout=timeout)
    
    def put_nowait(self, item: T) -> None:
        """ブロックせずに要素を追加"""
        super().put_nowait(item)
    
    def get_nowait(self) -> T:
        """ブロックせずに要素を取得"""
        return super().get_nowait()
    
    def __iter__(self):
        """キューの要素を順番に取得するイテレータ"""
        return iter(self._queue)