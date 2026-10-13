from typing import Final
from .base_player import BasePlayer
from poker import Move, Action


class CheckPlayer(BasePlayer):
    # A player that always checks/calls which is good as this means having two of these players will always go to showdown.
    def __init__(self, name: str, starting_money: int, BIG_BLIND: int):
        self.money = starting_money
        self._name = name
        self.BIG_BLIND: Final = BIG_BLIND

    def decision(self, history) -> Move:
        return Move(self, Action.CALL, history.last_move_amount)

    @property
    def name(self):
        return self._name

    def hand(self, cards):
        pass

    def preflop(self, cards):
        pass

    def flop(self, cards):
        pass

    def turn(self, card):
        pass

    def river(self, card):
        pass

    def placed_bet(self, amount):
        self.money -= amount

    def win(self, amount):
        self.money += amount

    def loose(self, winning_players_cards):
        pass
