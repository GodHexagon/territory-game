__package__ = "src"

from src.view import *
from src import pyxres
import pyxel
import sys
import os


class App:
    def __init__(self) -> None:
        if getattr(sys, 'frozen', False):
            # PyInstallerで実行されている場合
            resource_path = os.path.join(sys._MEIPASS, 'art', 'common.pyxpal'), os.path.join(sys._MEIPASS, 'art', 'common.pyxres') # type: ignore
        else:
            # 通常のPython実行時
            resource_path = os.path.join('..', 'art', 'common.pyxpal'), os.path.join('..', 'art', 'common.pyxres')

        PYXPAL_PATH = resource_path[0]
        PYXRES_PATH = resource_path[1]

        pyxel.init(768, 512, title="Territory Game", display_scale=1, fps=60)
        pyxel.mouse(True)
        pyxel.load(PYXRES_PATH)

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
