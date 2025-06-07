from enum import Enum
from players.base_player import BasePlayer
import random


# Enumarations used to represent the suits and ranks of a standard deck of 
# and makes it easier to iterate over them.
class Suit(Enum):
    SPADES = 'S'
    HEARTS = 'H'
    DIAMONDS = 'D'
    CLUBS = 'C'
    
class Rank(Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = 'T'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

class Card():
    __slots__ = ('rank', 'suit') #__slots__ is used to limit the attributes of the class

    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank.value}{self.suit.value}"

class Action(Enum):
    FOLD = 'fold'
    CALL = 'call'
    RAISE = 'raise'

class Move():
    __slots__ = ('player', 'action', 'amount')

    def __init__(self, player: BasePlayer, action: Action, amount: int):
        self.player = player
        self.action = action
        self.amount = amount
    
    def __repr__(self):
        return f"{self.action.value}{self.amount.value}"


def deck():
    all_cards = []
    for rank in Rank:
        for suit in Suit:
            all_cards.append(Card(rank, suit))
    random.shuffle(all_cards)  
    return all_cards

