from ..view import Area, View
from ..areas import *
from ...rule.rule import RuleQuad, Rotation, TilesMap, GameData
from pyxres import BLUE_COLOR_S, RED_COLOR_S, GREEN_COLOR_S, YELLOW_COLOR_S
from ...key_bind import *

class QuadGameView(Area, View):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        self.game = RuleQuad()
        self.game.set_on_change_pieces(self.hdl_change_pieces)
        self.game.set_on_end(self.hdl_end)
        self.game.set_on_give_up(self.hdl_give_up)

        self.rotation = Rotation.DEFAULT
        self.player_id = 0
        
        self.cursor = Cursor()

        board_view_end_y = int(y + h * 0.6)
        self.board = BoardView(
            x, 
            y, 
            w, 
            board_view_end_y, 
            self.cursor, 
            BLUE_COLOR_S,
            self.hdl_place_piece
        )
        self.picker = PickerView(
            0, 
            board_view_end_y + 1, 
            w, 
            h - board_view_end_y - 1, 
            self.game.get_pieces_shape(self.player_id),
            BLUE_COLOR_S,
            self.cursor
        )
        
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        self.notice = FrontNoticeView(x + w / 2 - 150, y + h * 0.3, 300, 50)
        self.notice.put('GAME START!', frame_to_hide=60)
    
    def hdl_place_piece(self, shape: TilesMap, rotation: Rotation, x: int, y: int):
        return self.game.place(shape, rotation, x, y)
    
    def hdl_change_pieces(self, player: int, data: GameData):
        if player == self.player_id:
            self.picker.reset_pieces(
                p.shape for p in data.pieces_by_player[player] if not p.placed()
            )
            held = self.cursor.held
            if held is not None:
                held.clear()
        self.board.rewrite_board(tuple(data.pieces_by_player), (BLUE_COLOR_S, RED_COLOR_S, GREEN_COLOR_S, YELLOW_COLOR_S))

    def hdl_end(self):
        scores = self.game.get_scores()
        if scores[0] < scores[1]: win = -1
        elif scores[0] > scores[1]: win = 1
        else: win = 0
        self.notice.put('Finish!')
    
    def hdl_give_up(self, player: int):
        if player != self.player_id:
            self.notice.put('THE ENEMY GAVE UP!')
    
    def update(self):
        if btnp(Bind.ROTATE_LEFT):
            self.rotation = Rotation.counter_cw(self.rotation)
        if btnp(Bind.ROTATE_RIGHT):
            self.rotation = Rotation.cw(self.rotation)
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        if btnp(Bind.GIVE_UP):
            self.game.give_up()

        self.picker.update()
        self.board.update()
        self.cursor.update()
        self.notice.update()
    
    def draw(self):
        self.board.draw()
        self.picker.draw()
        self.cursor.draw()
        self.notice.draw()
