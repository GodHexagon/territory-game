from typing import Tuple
from enum import Enum


class Rotation(Enum):
    DEFAULT = 0
    RIGHT1 = 1
    RIGHT2 = 2
    RIGHT3 = 3

class Piece:
    class Unplace:
        def __bool__():
            return False

    @staticmethod
    def instantiate_all():
        c = Piece
        return (
            c( ((0, 0)) ),
            c( ((0, 0), (0, 1)) ),
            c( ((0, 0), (0, 1), (0, 2)) ),
            c( ((0, 0), (0, 1), (1, 1)) ),
            c( ((0, 0), (0, 1), (0, 2), (0, 3)) ),
            c( ((0, 2), (1, 0), (1, 1), (1, 2)) ),
            c( ((0, 0), (0, 1), (0, 2), (1, 1)) ),
            c( ((0, 0), (0, 1), (1, 0), (1, 1)) ),
            c( ((0, 0), (0, 1), (1, 1), (1, 2)) ),
            c( ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4)) ),
            c( ((0, 3), (1, 0), (1, 1), (1, 2), (1, 3)) )
        )

    def __init__(self, shape: Tuple[Tuple[int, int]]):
        self.shape = shape
        self.position: Tuple[int, int] | Piece.Unplace = Piece.Unplace
        self.rotation: Rotation = Rotation.DEFAULT
    
class Game:
    class PlacePieceResult(Enum):
        OK = 0
        OVERHANG_BOARD = 1
        ALREADY_PLACED = 4
        COLLIDING = 2
        CORNER_RULE = 3
    
    @staticmethod
    def check(selection: Piece, cordinate_x: int, cordinate_y: int,  rotate: Rotation, src_board: Tuple[Tuple[int]]) -> PlacePieceResult:
        if (cordinate_x < 0 or
            cordinate_y < 0 or
            cordinate_x + selection.getSize() > len(src_board) or
            cordinate_y + selection.getSize() > len(src_board[0])
        ):
            e

    def __init__(self):
        self.players_pieces = { 0 : Piece.instantiate_all(), 1 : Piece.instantiate_all() }
        self.turn = 0

    def finish_turn(self):
        self.turn += 1
        if self.turn == len(self.players_pieces):
            self.turn = 0


if __name__ == '__main__':
    for p in Piece.instantiate_all():
        print(p.shape)
    g = Game()
    print(g.players_pieces[0][0].shape)
