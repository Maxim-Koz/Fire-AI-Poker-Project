from typing import Final 
from players.base_player import BasePlayer
from poker import Move, Action
import random

class RandomPlayer(BasePlayer):
    def __init__(self, name: str, starting_money: int, BIG_BLIND: int):
        self.error = None
        self.money = starting_money
        self.name = name
        self.BIG_BLIND: Final= BIG_BLIND 

    def decision(self, history) -> Move:

        actions = [Action.FOLD, Action.CALL, Action.RAISE]  
        if self.error is not None:
            actions.remove(Action.RAISE)  
        
        action = random.choice(actions)    
        if action == Action.FOLD:
            return Move(self, action, 0)
        elif action == Action.CALL:
            return Move(self, action, history.last_move_amount)  # dealer will handle the amount 
        elif action == Action.RAISE:
            raise_amount = random.randint(history.last_raise, self.money)
            return Move(self, action, raise_amount)
                
            


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

    def handle_error(self, error: str):
        self.error = error
