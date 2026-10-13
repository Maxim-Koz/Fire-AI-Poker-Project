from enum import Enum
import random


# Enumarations used to represent the suits and ranks of a standard deck of
# and makes it easier to iterate over them.
class Suit(Enum):
    SPADES = "S"
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"


class Rank(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


class Card:
    __slots__ = (
        "rank",
        "suit",
    )  # __slots__ is used to limit the attributes of the class

    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank.value} of {self.suit.value}"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


class Action(Enum):
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"


class Move:
    __slots__ = ("player", "action", "amount")

    def __init__(self, player, action: Action, amount: int):
        self.player = player
        self.action = action
        self.amount = amount

    def __str__(self):
        return f"{self.action.value}{self.amount}"


def deck():
    all_cards = []
    for rank in Rank:
        for suit in Suit:
            all_cards.append(Card(rank, suit))
    random.shuffle(all_cards)
    return all_cards
