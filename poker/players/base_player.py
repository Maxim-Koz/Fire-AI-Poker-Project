from abc import ABC, abstractmethod
from typing import Collection
from poker.history import History  
from poker import Card, Move       

# Abstract class for players so there is a standard interface all players must impliment
class BasePlayer(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def decision(self, history: History) -> Move:
        pass

    @abstractmethod
    def hand(self, cards: Collection[Card]): 
        pass

    @abstractmethod
    def flop(self, cards: Collection[Card]):
        pass

    @abstractmethod
    def turn(self, card: Card):
        pass

    @abstractmethod
    def river(self, card: Card):
        pass

    @abstractmethod
    def placed_bet(self,amount: int):
        pass

    @abstractmethod
    def win(self, amount: int):
        pass

