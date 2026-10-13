from typing import Final
from .base_player import BasePlayer
from poker import Move


class HumanPlayer(BasePlayer):
    def __init__(self, _name: str, starting_money: int, BIG_BLIND: int):
        self.money = starting_money
        self.money_given = 0
        self.BIG_BLIND: Final = BIG_BLIND
        self._name: Final = _name
        self.hand = []
        self.pending_move = None
        self.hole_cards = []

    @property
    def name(self) -> str:
        return self._name

    def decision(self, history) -> Move:
        move = self.pending_move
        self.pending_move = None
        return move

    def preflop(self, cards):
        self.hand = cards
        self.hole_cards = cards

    def flop(self, cards):
        self.hand.extend(cards)

    def turn(self, card):
        self.hand.append(card)

    def river(self, card):
        self.hand.append(card)

    def win(self, amount):
        self.money += amount

    def loose(self, players, winning_cards):
        self.money -= self.money_given

    def placed_bet(self, amount):
        pass
