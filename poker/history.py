from . import Move
class History():

    def __init__(self, BIG_BLIND: int):
        self.moves: list[Move] = []                     #store all moves made in the game
        self.last_move_amount = 0
        self.last_raise = BIG_BLIND

    def add_move(self, move: Move):
        self.moves.append(move)

    def overwrite_last_move(self, move: Move): # overwrite the last move made in the history
        self.moves[-1] = move





