class card():
    __slots__ = ('rank', 'suit')

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


crd = card('Ace', 'Spades')
print(crd)