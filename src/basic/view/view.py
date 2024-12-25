from abc import ABC, abstractmethod
from typing import Dict, Optional

class View(ABC):
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass
    
class ParenthoodView(View):
    def set_childs(self, childs: Dict[str, View]):
        self.childs = childs
    
    def update(self):
        for c in self.childs.values(): c.update()
    
    def draw(self):
        for c in self.childs.values(): c.draw()

class Area(ABC):
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def to_x(self, x: float):
        self.x = x
    
    def to_y(self, y: float):
        self.y = y
    
    def to_x_bottom(self, x: float):
        self.x = x - self.w
    
    def to_y_bottom(self, y: float):
        self.y = y - self.h
    
    def resize_to_end_x(self, x: float):
        self.w = x - self.x
    
    def resize_to_end_y(self, y: float):
        self.h = y - self.y
    
    def resize_to_start_x(self, x: float):
        self.w = self.x - x
        self.x = x
    
    def resize_to_start_y(self, y: float):
        self.h = self.y - y
        self.y = y

class CenteredArea(Area):
    def to_center_pos(self, cx: float, cy: float):
        self.x = cx - self.w / 2
        self.y = cy - self.h / 2
    
    def get_center_pos(self):
        return (self.x + self.w / 2, self.y + self.h / 2)
