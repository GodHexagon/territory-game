from basic.view import *
from typing import List
import pyxres
import pyxel


class App:
    def __init__(self) -> None:
        pyxel.init(768, 512, title="Territory Game", display_scale=1, fps=60)
        pyxel.mouse(True)
        pyxel.load(pyxres.PYXRES_PATH)

        self.scene = QuadGameView(0, 0, pyxel.width, pyxel.height)

        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_R) and pyxel.btn(pyxel.KEY_CTRL):
            self.scene = QuadGameView(0, 0, pyxel.width, pyxel.height)

        self.scene.update()

    def draw(self) -> None:
        pyxel.cls(0)
        self.scene.draw()


App()
