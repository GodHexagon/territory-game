from typing import Callable, Tuple
import pyxel
import enum

class Bind(enum.Enum):
    ROTATE_RIGHT = 1
    ROTATE_LEFT = 2

def btn(*args):
    return __agent(pyxel.btn, args)

def btnp(*args):
    return __agent(pyxel.btnp, args)

def __agent(f: Callable[[any], bool], args: Tuple[any]):
    a = args[1:]
    return (
        (args[0] == Bind.ROTATE_LEFT and (
            f(pyxel.KEY_D, *a) or f(pyxel.KEY_LEFT, *a)
        )) or
        (args[0] == Bind.ROTATE_RIGHT and (
            f(pyxel.KEY_F, *a) or f(pyxel.KEY_RIGHT, *a)
        ))
    )