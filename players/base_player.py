from abc import ABC, abstractmethod
from typing import Collection
from poker.history import History  
from poker import Card, Move       

# Abstract class for players so there is a standard interface all players must impliment
class Player(ABC):

    @abstractmethod
    def decision(self, history: History) -> Move:
        pass

    @abstractmethod
    def hand(self, cards: Collection[Card]): 
        pass

    @abstractmethod
    def flop(self, cards:Collection[Card]):
        pass

    @abstractmethod
    def turn(self, card: Card):
        pass

    @abstractmethod
    def river(self, card: Card):
        pass

    @abstractmethod
    def win(self, amount: int):
        pass

    @abstractmethod
    def draw(self, amount: int):
        pass

    @abstractmethod
    def handle_error(self, error: str):
        pass

