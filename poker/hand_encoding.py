import numpy as np
from numpy.typing import NDArray
from typing import Dict, List, Collection, Tuple
from . import Card, Suit, Rank

def parse_hand(hand: Collection[Card]) -> Tuple[Dict, List[int], List[Suit]]:
        RANK_ORDER = {rank: i for i, rank in enumerate(Rank, start=2)}  # mapping ranks to their order, starting from 2
        sorted_hand = sorted(hand, key=lambda card: RANK_ORDER[card.rank], reverse=True) # sort hand by rank
        ranks = [RANK_ORDER[card.rank] for card in sorted_hand]
        suits = [card.suit for card in sorted_hand] 
        return RANK_ORDER, ranks, suits 


def card_to_index(card: Card) -> int: # Maps a Card to an index from 0 to 51
    ranks = [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN,
             Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]
    suits = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]
    return ranks.index(card.rank) * 4 + suits.index(card.suit)

def onehot_hand(hand: Collection[Card]) -> NDArray[np.float64]:
        '''
        A 1D array of length 364 representing the one-hot encoding of a poker hand.
        '''
        num_slots = 7
        vec = np.zeros(num_slots * 52, dtype=np.float64)
        for i, card in enumerate(hand):
                vec[i * 52 + card_to_index(card)] = 1.0
        return vec
