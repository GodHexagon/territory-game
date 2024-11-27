from .limitter import LimitedDrawer
from .view import CenteredArea
from ..rule.rule import Piece, Rotation

from numpy import ndarray as NDArray
import numpy
from pyxel import Image as Image
import pyxel

from typing import *
from abc import ABC

from pyxres import TILE_SIZE_PX, TILE_COLOR_PALLET_NUMBER, DEFAULT_COLOR_S, BLOCK_TILE_COOR

class FollowablePiece:
    TILE_SCALE = 2

    def __init__(self, piece: Piece, piece_color_s: int, holder: 'PieceHolder'):
        self.piece = piece
        self.piece_color_s = piece_color_s
        self.follow(holder)
        self.visibility = True
        
        images: List[pyxel.Image] = []

        for by_direction_sequence in range(4):
            rotated = piece.copy_rotated_right90(by_direction_sequence)

            image = pyxel.Image(rotated.get_width() * TILE_SIZE_PX, rotated.get_height() * TILE_SIZE_PX)
            for i in range(TILE_COLOR_PALLET_NUMBER): image.pal(i + DEFAULT_COLOR_S, i + piece_color_s)

            for (row, col), value in numpy.ndenumerate(rotated.shape):
                if value == Piece.TILED:
                    image.blt(
                        col * TILE_SIZE_PX,
                        row * TILE_SIZE_PX,
                        pyxel.image(0),
                        BLOCK_TILE_COOR[0], 
                        BLOCK_TILE_COOR[1], 
                        TILE_SIZE_PX,
                        TILE_SIZE_PX,
                    )
            images.append(image)
        self.images = images
    
    def draw(self, piece_rotation: Rotation, drawer: LimitedDrawer):
        if not self.visibility:
            return

        if piece_rotation == Rotation.RIGHT_90:
            image = self.images[1]
        elif piece_rotation == Rotation.RIGHT_180:
            image = self.images[2]
        elif piece_rotation == Rotation.RIGHT_270:
            image = self.images[3]
        else:
            image = self.images[0]
        
        f = self.followings
        c = f.get_center_pos()
        f.w = image.width
        f.h = image.height
        f.to_center_pos(c[0], c[1])

        T = FollowablePiece.TILE_SCALE
        drawer.lblt(
            c[0] - T * (image.width / 2),
            c[1] - T * (image.height / 2),
            image,
            0, 0, image.width, image.height,
            colkey=0,
            scale=T
        )
    
    def follow(self, holder: 'PieceHolder'):
        holder.hold(self)
        self.followings = holder
    
    def set_visibility(self, value: bool):
        self.visibility = value
    
class PieceHolder(CenteredArea):
    def hold(self, piece: Optional[FollowablePiece] = None):
        self.held = piece
    
    def is_holding(self):
        return self.held is not None
