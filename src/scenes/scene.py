from abc import ABC, abstractmethod
from typing import Callable

class Scene(ABC):
    def __init__(self, switch_scene : Callable):
        self.switch_scene = switch_scene

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass
