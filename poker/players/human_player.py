from typing import Final 
from .base_player import BasePlayer
from poker import Move, Action


class RandomPlayer(BasePlayer):
    def __init__(self, _name: str, starting_money: int, BIG_BLIND: int):
        self.money = starting_money
        self.money_given = 0
        self.BIG_BLIND: Final = BIG_BLIND 
        self._name = _name

    @property
    def name(self) -> str:
        return self._name

    def decision(self, history) -> Move: 
        print(f"last rasise was {history.last_raise}, last move was {history.moves[-1] if history.moves else 'None'}")
        while True:
            action = input("Enter your action (see cards, see history, call , raise (amount), fold), (call, raise and fold will end your turn): ").strip().lower()

    def hand(self, cards):
        print(f"{self.name} received hand: {cards}")

    def flop(self, cards):
        print(f"{self.name} sees flop: {cards}")

    def turn(self, card):
        print(f"{self.name} sees turn: {card}")

    def river(self, card):
        print(f"{self.name} sees river: {card}")

    def win(self, amount):
        self.money += amount
        print(f"{self.name} wins {amount}. Current money: {self.money}, money won: {amount}, change in money: {amount - self.money_given}")

    def loose(self, players, winning_cards):
        pass