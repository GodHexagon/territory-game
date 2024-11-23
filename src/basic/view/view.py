from abc import ABC, abstractmethod
from typing import Dict

class View(ABC):
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class Area(ABC):
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class CenteredArea(Area):
    def to_center_pos(self, cx:float, cy:float):
        self.x = cx - self.w / 2
        self.y = cy - self.h / 2
    
    def get_center_pos(self):
        return (self.x + self.w / 2, self.y + self.h / 2)
    
class ParenthoodView(View):
    def __init__(self, childs: Dict[str, View]):
        self.childs = childs
    
    def update(self):
        for c in self.childs.values(): c.update()
    
    def draw(self):
        for c in self.childs.values(): c.draw()
