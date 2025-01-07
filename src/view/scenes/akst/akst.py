from ...base.view import View, Area
from src.pyxres import *
from ...areas.text import WritenText
from ...areas.button import TextButton
from ...areas.textfield import TextField
from ...sequencer.access_key import AccessKeyManager

import pyxel

from typing import *

class AccessKeySettingScene(View, Area):
    def __init__(self, x: float, y: float, w: float, h: float, on_complete: Callable[[bool], None]) -> None:
        super().init_area(x, y, w, h)
        self.window = Window(*self.get_center_pos(), on_complete)
    
    def update(self):
        self.window.update()

    def draw(self):
        pyxel.cls(COLOR_WHITE)
        self.window.draw()

class Window(Area):
    SIZE_PX = (500, 200)
    MARGIN_PX = 16

    def __init__(self, cx: float, cy: float, on_complete: Callable[[bool], None]) -> None:
        self.init_unplaced_area(*Window.SIZE_PX)
        self.to_center_pos(cx, cy)

        self.on_complete = on_complete

        MARGIN = Window.MARGIN_PX

        self.title = WritenText(cx, 0, text="SET YOUR ACCESS KEY", color=COLOR_BLACK, scale=5)
        self.title.to_y(self.y + MARGIN)

        self.console: WritenText | TextField = WritenText(cx, cy, "PROCESSING...", COLOR_FAILURE)

        self.update_b = TextButton(0, 0, self.__hdl_try_to_complete, "UPDATE")
        self.update_b.set_enabled(False)
        self.update_b.set_colors(backgroud=COLOR_SUCCESSFULL)
        self.update_b.to_x_end(self.x + self.w - MARGIN)
        self.update_b.to_y_bottom(self.y + self.h - MARGIN)
        
        self.cancel_b = TextButton(0, 0, lambda : on_complete(False), "CANCEL")
        self.cancel_b.to_x(self.x + MARGIN)
        self.cancel_b.to_y_bottom(self.y + self.h - MARGIN)
        
        self.akm = AccessKeyManager(self.__hdl_throw_error, self.__hdl_load_current_sk, self.__hdl_save_complete)
        ok = self.akm.load()
        if not ok: raise RuntimeError("予期しないリソースの競合。画面の開始と完了が非常に近かった可能性がある。")
    
    def __hdl_try_to_complete(self):
        self.update_b.set_enabled(False)
        c = self.console
        if isinstance(c, TextField):
            ok = self.akm.save(c.get_text())
        else:
            RuntimeError("このタイミングの完了ボタン押下は禁止されている。")
        if not ok: raise RuntimeError("予期しないリソースの競合。画面の開始と完了が非常に近かった可能性がある。")
    
    def __hdl_throw_error(self):
        self.console = WritenText(*self.get_center_pos(), "ERROR", COLOR_FAILURE)

    def __hdl_load_current_sk(self, value: str):
        self.update_b.set_enabled(True)

        MARGIN = Window.MARGIN_PX
        self.console = TextField(lambda _: None, value)
        self.console.set_w(self.w - MARGIN * 2)
        self.console.to_center_pos(*self.get_center_pos())
    
    def __hdl_save_complete(self):
        self.on_complete(True)
    
    def update(self):
        if isinstance(self.console, TextField):
            self.console.update()
        self.update_b.update()
        self.cancel_b.update()
        self.akm.update()
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.title.draw()
        self.console.draw()
        self.update_b.draw()
        self.cancel_b.draw()
