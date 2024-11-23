from basic.view import *
from typing import List
import pyxel

class App:
    def __init__(self):
        pyxel.init(768, 512, title="Territory Game", display_scale=2)
        pyxel.mouse(True)
        pyxel.load('../art/common.pyxres')

        self.view = GameView(0, 0, pyxel.width, pyxel.height)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.view.update()

    def draw(self):
        pyxel.cls(0)
        self.view.draw()


App()
