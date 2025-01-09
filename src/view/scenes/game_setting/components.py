from ...areas.text import WritenText
from ...base.limitter import LimitableArea
from ...base.view import View, Area, CenteredArea
from ..player_type import PlayerType
from ....data.player_color import PLAYER_COLORS
from ...areas.button import IconButton, TextButton
from src.pyxres import *

import pyxel
import pyperclip # type: ignore

from typing import *

class SceneData:
    TEXT_COLOR = COLOR_BLACK
    BACKGROUND_COLOR = COLOR_WHITE

    COMUNM_NAMES_Y = 80

    ROW_HEIGHT_PX = 56
    ROW_GAP_PX = 8

    LEFT_MARGIN_PX = 32

    PLAYABLE_CENTER_X = 192
    AI_CENTER_X = 256
    UNASSIGNED_CENTER_X = 320
    MULTIPLAY_CENTER_X = 400
    PASSWORD_START_X = 470
    
    PLAYER_COLORS = PLAYER_COLORS

class ProgressingIndicator(WritenText):
    def __init__(self, cx, cy, scale = 3, parent_surface = None, visible: bool = False):
        super().__init__(cx, cy, "CONNECTING TO SERVER.", COLOR_FAILURE, scale, parent_surface)
        self.animation_sequence = 0
        self.set_visible(visible)
    
    def update(self):
        new_seq = (pyxel.frame_count // 30) % 3
        if self.animation_sequence != new_seq:
            self.rewrite("CONNECTING TO SERVER" + "."*(new_seq + 1), COLOR_FAILURE)
            self.animation_sequence = new_seq
    
    def set_visible(self, visible: bool):
        self.visible = visible
    
    def draw(self):
        if self.visible: super().draw()

class Player(LimitableArea):
    HEIGHT_PX = SceneData.ROW_HEIGHT_PX

    def __init__(self, x, y, w, 
            label: str, 
            label_color: int, 
            on_change: Callable[[PlayerType], None], 
            default: PlayerType = PlayerType.AI
        ):
        super().init_area(x, y, w, Player.HEIGHT_PX)
        self.set_limiteds()

        self.on_change = on_change
        self.type = default

        self.label = WritenText(0, y + self.h / 2, label, label_color, scale=3)
        self.label.x = x + 16
    
    def ini_radios(self, multiplay: bool = False) -> Tuple['RadioButton', ...]:
        PCX = SceneData.PLAYABLE_CENTER_X
        ACX = SceneData.AI_CENTER_X
        UCX = SceneData.UNASSIGNED_CENTER_X
        MCX = SceneData.MULTIPLAY_CENTER_X
        Y = self.y + self.h / 2
        self.buttons: Tuple[RadioButton, ...] = (
            RadioButton(PCX, Y, self.__hdl_click_playable, self.type == PlayerType.PLAYABLE),
            RadioButton(ACX, Y, self.__hdl_click_ai, self.type == PlayerType.AI),
            RadioButton(UCX, Y, self.__hdl_click_unassigned, self.type == PlayerType.UNASSIGNED)
        )
        if multiplay: self.buttons += (RadioButton(MCX, Y, self.__hdl_click_multiplayer, self.type == PlayerType.MULTIPLAYER), )

        return self.buttons
    
    def set_player_type(self, player_type: PlayerType):
        self.type = player_type
        ASSIGNMENT = (PlayerType.PLAYABLE, PlayerType.AI, PlayerType.UNASSIGNED, PlayerType.MULTIPLAYER)
        for i, b in enumerate(self.buttons):
            b.set_selected(player_type == ASSIGNMENT[i])
    
    def __hdl_click_playable(self):
        self.on_change(PlayerType.PLAYABLE)
    
    def __hdl_click_ai(self):
        self.on_change(PlayerType.AI)
    
    def __hdl_click_unassigned(self):
        self.on_change(PlayerType.UNASSIGNED)
    
    def __hdl_click_multiplayer(self):
        self.on_change(PlayerType.MULTIPLAYER)
    
    def draw(self):
        self.drawer.rect(self.x, self.y, self.w, self.h, COLOR_PRIMARY)
        self.label.draw()

class RadioButton(CenteredArea, LimitableArea, View):
    RADIUS_PX = 16

    def __init__(self, cx, cy, on_click: Callable[[], None], default: bool = False):
        super().init_area(0, 0, self.RADIUS_PX, self.RADIUS_PX)
        self.to_center_pos(cx, cy)
        self.set_limiteds()
        self.selected = default
        self.on_click = on_click
    
    def set_selected(self, selected: bool):
        self.selected = selected
    
    def update(self):
        if self.input.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.on_click()
    
    def draw(self):
        LINE = SceneData.TEXT_COLOR
        EMPTY = SceneData.BACKGROUND_COLOR
        cx, cy = self.get_center_pos()
        self.drawer.circ(cx, cy, self.RADIUS_PX // 2, EMPTY)
        self.drawer.circb(cx, cy, self.RADIUS_PX // 2, LINE)
        if self.selected:
            self.drawer.circ(cx, cy, self.RADIUS_PX // 4, LINE)
            
class ReadonlyText(Area):
    ICON_SIZE_PX = 24
    MARGIN_PX = 8
    GAP_PX = 8
    MIN_WIDTH = 128

    def __init__(self, on_changed: Callable[[str], None], default: str = ""):
        IS = ReadonlyText.ICON_SIZE_PX
        MARGIN = ReadonlyText.MARGIN_PX

        self.on_changed = on_changed

        self.init_unplaced_area(self.MIN_WIDTH, IS + MARGIN * 2)

        self.text = default
        self.field = TextButton(0, 0, lambda: None, default)
        
        TX, TY = COPY_ICON_COOR
        self.copy_b = IconButton(
            0, 0, size=IS, on_click=self.__hdl_copy,
            tile_selector=(TX, TY, TILE_SIZE_PX, TILE_SIZE_PX)
        )

        self.set_colors()
    
    def get_text(self):
        return self.text
        
    def to_x(self, x):
        diff = x - self.x
        super().to_x(x)
        self.field.to_x(x + self.MARGIN_PX)
        self.copy_b.to_x(self.copy_b.x + diff)

    def to_y(self, y):
        super().to_y(y)
        self.field.to_y(y + ((self.MARGIN_PX * 2 + self.ICON_SIZE_PX) - self.field.h) / 2)
        self.copy_b.to_y(y + self.MARGIN_PX)
    
    def set_w(self, w):
        w = max(w, self.MIN_WIDTH)
        super().set_w(w)
        self.field.set_w(w - self.MARGIN_PX * 2 - self.ICON_SIZE_PX)
        self.copy_b.to_x(self.x + w - self.MARGIN_PX - self.ICON_SIZE_PX)
    
    def set_h(self, h):
        raise ValueError("このコンポーネントは高さを変更できない。")
    
    def set_colors(self, fill: int = COLOR_BLACK, background: int = COLOR_PRIMARY):
        self.background = background
        self.field.set_colors(text=fill, backgroud=background, border=background)
        self.copy_b.set_colors(text=fill, backgroud=background, border=background)
        self.to_x(self.x)
        self.to_y(self.y)
        self.set_w(self.w)

    def __hdl_copy(self):
        pyperclip.copy(self.text)

    def update(self):
        self.copy_b.update()
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, self.background)
        self.field.draw()
        self.copy_b.draw()
