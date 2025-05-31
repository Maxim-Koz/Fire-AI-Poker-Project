class Card():
    __slots__ = ('rank', 'suit') #__slots__ is used to limit the attributes of the class

    def __init__(self, rank :str, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


crd = Card('Ace', 'Spades')
print(crd)

