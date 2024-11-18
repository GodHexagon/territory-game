import pyxel
from typing import Callable
from scenes.scene import Scene

class Game(Scene):
    def __init__(self, switch_scene : Callable[[Scene], None]):
        super().__init__(switch_scene)

    def update(self):
        pass
    
    def draw(self):
        pyxel.cls(1)
        pyxel.text(55, 41, "In the Game!", pyxel.frame_count % 16)
