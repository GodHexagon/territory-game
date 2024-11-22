from view import *
from typing import List
import pyxel

class App:
    def __init__(self):
        pyxel.init(768, 512, title="Territory Game", display_scale=2)
        pyxel.mouse(True)

        pyxel.load('../art/common.pyxres')

        board_view_end_y = int(pyxel.height * 0.6)
        self.views:List[Displayable] = [
            BoardView(0, 0, pyxel.width, board_view_end_y),
            PickerView(0, board_view_end_y + 1, pyxel.width, pyxel.height - board_view_end_y - 1)
        ]

        pyxel.run(self.update, self.draw)

    def update(self):
        for v in self.views:
            v.update()

    def draw(self):
        pyxel.cls(0)
        for v in self.views:
            v.draw()


App()
