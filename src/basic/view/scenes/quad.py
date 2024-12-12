from ..view import Area, View
from ..areas import *
from ...rule.rule import Rule4Player, Rotation, TilesMap, GameData, PlacementResult, EventLogger
from pyxres import BLUE_COLOR_S, RED_COLOR_S, GREEN_COLOR_S, YELLOW_COLOR_S
from ...key_bind import *

class QuadGameView(Area, View):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

        self.game = Rule4Player()

        self.rotation = Rotation.DEFAULT
        self.players = [('YOU', BLUE_COLOR_S), ('RED PLAYER', RED_COLOR_S), ('GREEN PLAYER', GREEN_COLOR_S), ('YELLOW PLAYER', YELLOW_COLOR_S)]
        self.player_id = 0
        
        self.cursor = Cursor()

        board_view_end_y = int(y + h * 0.6)
        self.board = BoardView(
            x, 
            y, 
            w, 
            board_view_end_y, 
            self.cursor, 
            self.players[self.player_id][1],
            self.hdl_place_piece
        )
        self.picker = PickerView(
            0, 
            board_view_end_y + 1, 
            w, 
            h - board_view_end_y - 1, 
            self.game.get_pieces_shape(self.player_id),
            self.players[self.player_id][1],
            self.cursor
        )
        
        self.result = ResultWindow(x + (w - 300) / 2, board_view_end_y - 100, 300, 200)
        
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        self.notice = FrontNoticeView(x + w / 2 - 150, y + h * 0.3, 300, 50)
        self.notice.put('GAME START!', frame_to_hide=60)
    
    def __turn_end(self, log: EventLogger):
        while self.game.get_turn() != self.player_id and not self.game.is_end():
            _, l = self.game.ai_place()
            log.append(l)
        
        self.__commmon_event_handler(log)
    
    def __commmon_event_handler(self, log: EventLogger):
        data = log.data

        cpbp = log.changed_piece_by_player
        if cpbp.__len__() > 0: 
            if self.player_id in cpbp:
                self.picker.reset_pieces(
                    p.shape for p in data.pieces_by_player[self.player_id] if not p.placed()
                )
                held = self.cursor.held
                if held is not None:
                    held.clear()
            self.board.rewrite_board(tuple(data.pieces_by_player), tuple(c for _, c in self.players))
        
        g_p = log.gave_up_player
        if g_p.__len__() == 1:
            name, color = self.players[g_p.pop()]
            self.notice.put(f'{name} GAVE UP!', color=color)
        elif g_p.__len__() > 1:
            self.notice.put('SOME PEOPLE GAVE UP!')
        
        if log.ended:
            scores = self.game.get_scores()
            ps = scores[self.player_id]
            if any([s > ps for s in scores]): win = -1
            elif scores.count(ps) > 1: win = 0
            else: win = 1
            self.result.show(
                [(f"{name}: {score}", color) for (name, color), score in zip(self.players, scores)],
                win
            )
    
    def hdl_place_piece(self, shape: TilesMap, rotation: Rotation, x: int, y: int):
        if self.game.get_turn() == GameData.END_STATE_TURN: return False
        if self.game.get_turn() != self.player_id: raise RuntimeError('ターンが不正である。')

        success = False
        if self.game.get_turn() == self.player_id:
            r, l = self.game.place(shape, rotation, x, y)
            success = r == PlacementResult.SUCCESS
            
            self.__turn_end(l)

        return success
    
    def hdl_give_up(self):
        if self.game.get_turn() == self.player_id:
            _, l = self.game.give_up()

            self.__turn_end(l)
    
    def update(self):
        if btnp(Bind.ROTATE_LEFT):
            self.rotation = Rotation.counter_cw(self.rotation)
        if btnp(Bind.ROTATE_RIGHT):
            self.rotation = Rotation.cw(self.rotation)
        self.picker.set_piece_rotation(self.rotation)
        self.board.set_piece_rotation(self.rotation)
        self.cursor.set_rotation(self.rotation)

        if btnp(Bind.GIVE_UP):
            self.hdl_give_up()

        self.picker.update()
        self.board.update()
        self.notice.update()
        self.result.update()
        self.cursor.update()
    
    def draw(self):
        self.board.draw()
        self.picker.draw()
        self.notice.draw()
        self.result.draw()
        self.cursor.draw()
