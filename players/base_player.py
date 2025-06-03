from abc import ABC, abstractmethod
from ..poker.history import History

# Abstract class for players so there is a standard interface all players must impliment
class Player(ABC):

    @abstractmethod
    def hand(self):
        pass

    @abstractmethod
    def flop(self):
        pass

    @abstractmethod
    def turn(self):
        pass

    @abstractmethod
    def river(self):
        pass

    @abstractmethod
    def decision(self, history):
        pass

