import pyxel
from scenes import Scene, Title

class App:
    def __init__(self):
        pyxel.init(384, 256, title="Territory Game")
        self.scene : Scene = Title(self.switch_scene)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
    
    def switch_scene(self, new_instance : Scene):
        self.scene = new_instance

App()
