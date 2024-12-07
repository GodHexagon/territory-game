from typing import Callable, Tuple
import pyxel
import enum

class Bind(enum.Enum):
    SEIZE_PIECE = 0
    ROTATE_RIGHT = 1
    ROTATE_LEFT = 2
    PLACE_PIECE = 3
    GIVE_UP = 4

def btn(*args):
    return __agent(pyxel.btn, args)

def btnp(*args):
    return __agent(pyxel.btnp, args)

def __agent(f: Callable[[any], bool], args: Tuple[any]): # type: ignore
    a = args[1:]
    return (
        (args[0] == Bind.ROTATE_LEFT and (
            f(pyxel.KEY_D, *a) or f(pyxel.KEY_LEFT, *a)
        )) or
        (args[0] == Bind.ROTATE_RIGHT and (
            f(pyxel.KEY_F, *a) or f(pyxel.KEY_RIGHT, *a)
        )) or
        (args[0] == Bind.SEIZE_PIECE and (
            f(pyxel.MOUSE_BUTTON_LEFT, *a)
        )) or
        (args[0] == Bind.PLACE_PIECE and (
            f(pyxel.MOUSE_BUTTON_LEFT, *a)
        )) or
        (args[0] == Bind.GIVE_UP and (
            f(pyxel.KEY_G, *a) and pyxel.btn(pyxel.KEY_CTRL)
        ))
    )
