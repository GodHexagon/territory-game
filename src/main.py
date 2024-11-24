from basic.game import GameView
from typing import List
import pyxres
import pyxel


class App:
    def __init__(self):
        pyxel.init(768, 512, title="Territory Game", display_scale=2)
        pyxel.mouse(True)
        pyxel.load(pyxres.PYXRES_PATH)

        self.view = GameView(0, 0, pyxel.width, pyxel.height)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.view.update()

    def draw(self):
        pyxel.cls(0)
        self.view.draw()


App()
