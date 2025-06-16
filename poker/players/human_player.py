from typing import Final 
from .base_player import BasePlayer
from poker import Move, Action


class RandomPlayer(BasePlayer):
    def __init__(self, name: str, starting_money: int, BIG_BLIND: int):
        self.money = starting_money
        self.money_given = 0
        self.name = name
        self.BIG_BLIND: Final= BIG_BLIND 

    def decision(self, history) -> Move:
        pass

    def hand(self, cards):
        pass

    def flop(self, cards):
        pass

    def turn(self, card):
        pass

    def river(self, card):
        pass

    def win(self, amount):
        self.money += amount
        print(f"{self.name} wins {amount}. Current money: {self.money}, money won: {amount}")

    def draw(self, amount):
        self.money += amount
        print(f"{self.name} draws {amount}. Current money: {self.money}, money drawn: {amount}")