from pyxel import Image
import pyxel
from typing import *

class TextDrawable:
    from src.pyxres import CHAR_HEIGHT_PX, CHAR_WIDTH_PX
    
    @staticmethod
    def generate_text_image(value: str, color: int, background_color: int) -> Image:
        t_w = max(0, len(value) * TextDrawable.CHAR_WIDTH_PX - 1)
        img = Image(t_w, TextDrawable.CHAR_HEIGHT_PX)
        img.cls(background_color)
        img.text(0, 0, value, color, None)
        return img
    
    @staticmethod
    def get_args_draw_text(img: Image, cx: float, cy: float) -> Tuple[float, float, Image, float, float, float, float]:
        return (
            cx - img.width / 2,
            cy - img.height / 2,
            img,
            0, 0, img.width, img.height
        )
