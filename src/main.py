from basic.view import *
from typing import List
import pyxres
import pyxel


class App:
    def __init__(self) -> None:
        pyxel.init(768, 512, title="Territory Game", display_scale=1, fps=60)
        pyxel.mouse(True)
        pyxel.load(pyxres.PYXRES_PATH)

        self.__init_game()

        pyxel.run(self.update, self.draw)
    
    def __init_game(self):
        self.view = MainView(0, 0, pyxel.width, pyxel.height)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_R) and pyxel.btn(pyxel.KEY_CTRL):
            self.__init_game()

        self.view.update()

    def draw(self) -> None:
        pyxel.cls(0)
        self.view.draw()


App()
