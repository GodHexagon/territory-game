import pyxel
from typing import Callable
from scenes.scene import Scene
from scenes.game import Game

class Title(Scene):
    def __init__(self, switch_scene : Callable[[Scene], None]):
        self.switch_scene = switch_scene
        self.name = "Title"

    def update(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.switch_scene(Game())
    
    def draw(self):
        pyxel.cls(0)
        pyxel.text(55, 41, "This is {}!".format(self.name), pyxel.frame_count % 16)