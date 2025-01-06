from abc import ABC, abstractmethod
from typing import *

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
    def init_area(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def to_x(self, x: float):
        self.x = x
    
    def to_y(self, y: float):
        self.y = y
    
    def to_x_end(self, x: float):
        self.to_x(x - self.w)
    
    def to_y_bottom(self, y: float):
        self.to_y(y - self.h)
        
    def set_w(self, w: float):
        self.w = w
    
    def set_h(self, h: float):
        self.h = h
    
    def resize_to_end_x(self, x: float):
        self.set_w(x - self.x)  # set_w を活用
    
    def resize_to_bottom_y(self, y: float):
        self.set_h(y - self.y)  # set_h を活用
    
    def resize_to_start_x(self, x: float):
        self.set_w(self.x - x)
        self.to_x(x)  # to_x を活用
    
    def resize_to_top_y(self, y: float):
        self.set_h(self.y - y)
        self.to_y(y)  # to_y を活用
        
    def to_center_pos(self, cx: float, cy: float) -> None:
        self.to_x(cx - self.w / 2)  # to_x を活用
        self.to_y(cy - self.h / 2)  # to_y を活用
    
    def get_center_pos(self) -> Tuple[float, float]:
        return (self.x + self.w / 2, self.y + self.h / 2)

class MovableArea(Area):
    def init_area(self, x, y, w, h):
        self.to_x(x)
        self.to_y(y)
        self.set_w(w)
        self.set_h(h)

    def secrecy_init_area(self):
        self.x, self.y, self.w, self.h = 0, 0, 0, 0

class CenteredArea(Area):
    pass
