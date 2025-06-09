from enum import Enum

class PlayerType(Enum):
    HOST = 0
    JOIN = 1
    AI = 2

class Color(Enum):
    BLUE = 0
    RED = 1
    GREEN = 2
    YELLOW = 3

class PlayerData:
    def __init__(self, name: str, type: PlayerType, color: Color):
        self.name = name
        self.type = type
        self.color = color
