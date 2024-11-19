import pyxel
from view import BoardView

class App:
    def __init__(self):
        pyxel.init(768, 512, title="Territory Game")
        pyxel.mouse(True)

        pyxel.colors.from_list([
            0x000000,
            0xdcdcdc,
            0xa9a9a9,
            0x808080
        ])

        self.views = [BoardView(0, 0, pyxel.width, pyxel.height * 0.7)]

        pyxel.run(self.update, self.draw)

    def update(self):
        for v in self.views:
            v.update()

    def draw(self):
        pyxel.cls(0)
        for v in self.views:
            v.draw()


App()
