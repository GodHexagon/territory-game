from basic.view.scenes.vsai import VSAIGameView
from typing import List
import pyxres
import pyxel


class App:
    def __init__(self):
        pyxel.init(768, 512, title="Territory Game", display_scale=1, fps=60)
        pyxel.mouse(True)
        pyxel.load(pyxres.PYXRES_PATH)

        self.scene = VSAIGameView(0, 0, pyxel.width, pyxel.height)

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_R) and pyxel.btn(pyxel.KEY_CTRL):
            self.scene = VSAIGameView(0, 0, pyxel.width, pyxel.height)

        self.scene.update()

    def draw(self):
        pyxel.cls(0)
        self.scene.draw()


App()
