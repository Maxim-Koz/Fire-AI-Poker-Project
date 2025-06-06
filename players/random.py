from typing import Final
from .base_player import BasePlayer
from poker import Move
import random

class RandomPlayer(BasePlayer):
    def __init__(self, starting_money: int, name: str, BIG_BLIND: int):
        self.money = starting_money
        self.name = name
        self.BIG_BLIND: Final= BIG_BLIND 

    def decision(self, history) -> Move:
        actions = ['fold', 'call', 'raise']
        action = random.sample(actions, 1)[0]
        while True:
            if action == 'fold':
                return Move(self, action, )


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

    def draw(self, amount):
        self.money += amount

    def handle_error(self, error):
        self.error = error
