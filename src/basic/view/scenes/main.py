from ..view import View, Area
from .quad import PlayersType, SingleplayGameScene

import pyxel

class MainView(View, Area):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        PT = PlayersType
        self.scene = SingleplayGameScene(
            0, 0, pyxel.width, pyxel.height,
            [
                (PT.AI, 'P1'),
                (PT.PLAYABLE, 'YOU'),
                (PT.AI, 'P2'),
                (PT.AI, 'P3'),
            ]
        )
    
    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
