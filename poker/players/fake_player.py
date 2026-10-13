from typing import Final, Collection, Dict
from .base_player import BasePlayer
from poker import Move, Action, Card


class FakePlayer(BasePlayer):
    """A fake player that will call until the turn, then fold."""

    def __init__(self, name: str, starting_money: int, BIG_BLIND: int):
        self.money = starting_money
        self._name = name
        self.BIG_BLIND: Final = BIG_BLIND
        self.current_round = None

    def decision(self, history) -> Move:
        return Move(self, Action.FOLD, 0)

    @property
    def name(self):
        return self._name

    def preflop(self, cards: Collection[Card]):
        self.current_round = "preflop"

    def flop(self, cards: Collection[Card]):
        self.current_round = "flop"

    def turn(self, card: Card):
        self.current_round = "turn"

    def river(self, card: Card):
        self.current_round = "river"

    def placed_bet(self, amount: int):
        self.money -= amount

    def win(self, amount: int):
        self.money += amount
        print(f"{self.name} wins {amount}, total money: {self.money}")

    def loose(self, winning_players_cards: Dict):
        print(f"{self.name} final money: {self.money}")
