from abc import ABC, abstractmethod

# ViewAreas
class ViewArea(ABC):
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass
