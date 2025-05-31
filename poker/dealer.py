from typing import Sequence
from . import deck, Card

class Player: 
    pass

class Dealer():
    def __init__(self, players: Sequence[Player]):
        self.players = players
    
    def play(self):
        pass

        
print(deck())