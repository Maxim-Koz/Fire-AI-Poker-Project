from typing import Dict, List, Collection, Tuple
from . import Card, Suit, Rank

def parse_hand(hand: Collection[Card]) -> Tuple[Dict, List[int], List[Suit]]:
        RANK_ORDER = {rank: i for i, rank in enumerate(Rank, start=2)}  # mapping ranks to their order, starting from 2
        sorted_hand = sorted(hand, key=lambda card: RANK_ORDER[card.rank], reverse=True) # sort hand by rank
        ranks = [RANK_ORDER[card.rank] for card in sorted_hand]
        suits = [card.suit for card in sorted_hand] 
        return RANK_ORDER, ranks, suits 