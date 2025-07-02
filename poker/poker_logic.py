from typing import Dict, List, Collection, Tuple
from collections import Counter
from . import Card, Suit, Rank

def showdown(hands: Dict[str, List[Card]]) -> List[str]: #handles showdown logic
    return ["make it work later"]

def parse_hand(self, hand: Collection[Card]) -> Tuple[List[int], List[Suit]] :
        RANK_ORDER = {rank: i for i, rank in enumerate(Rank, start=2)}  # mapping ranks to their order, starting from 2
        ranks = sorted((RANK_ORDER[card.rank] for card in hand), reverse=True)
        suits = [card.suit for card in hand] 
        return ranks, suits 
    
def is_straight(self, ranks: List[int]) -> bool: 
    dif = 0
    for i in range(len(ranks)):
        if i !=0 and ranks[i] != ranks[i-1] - 1:
            dif += 1

    if dif == 4 or ranks == [14, 5, 4, 3, 2]:
        return True
    else:
        return False
    
def most_common_rank(self, ranks: List[int]) -> Tuple[int, List[int]]:   

    rank_counts = Counter(ranks)          
    max_rank_frequency = max(rank_counts.values())

    #find all values with that frequency
    most_common_ranks = [rank for rank, count in rank_counts.items() if count == max_rank_frequency]

    return max_rank_frequency, most_common_ranks


def evaluate_hand(self, hand: Collection[Card]) -> int:
    #gives value based on hand rating, higher is better

    ranks, suits = self.parse_hand(hand)
    max_rank_frequency, most_common_ranks = self.most_common_rank(ranks)


    if len(set(suits)) == 1 and self.is_straight(ranks): #straight flush
        return 8
    if max_rank_frequency == 4: # four of a kind
        return 7
    if (ranks.count(ranks[0]) == 3 and ranks.count(ranks[4]) == 2) or (ranks.count(ranks[0]) == 2 and ranks.count(ranks[4]) == 3): # full house
        return 6
    if len(set(suits)) == 1: # flush
        return 5
    if self.is_straight(ranks): # straight
        return 4
    if max_rank_frequency == 3: # three of a kind
        return 3
    if max_rank_frequency == 2 and len(most_common_ranks) == 2: # two pair
        return 2
    if max_rank_frequency == 2: # one pair
        return 1
    return 0 

def final(self, hand1: Collection[Card], hand2: Collection[Card]):
    value1 = self.evaluate_hand(hand1)
    value2 = self.evaluate_hand(hand2)

    if value1 > value2:
        return [hand1]
    elif value2 > value1:
        return [hand2]
    else:
        ranks1, _ = self.parse_hand(hand1)
        ranks2, _ = self.parse_hand(hand2)
        ranks1 = ranks1[:5]
        ranks2 = ranks2[:5]
        compare_high_cards = ranks1 if ranks1 > ranks2 else ranks2 if ranks1 < ranks2 else "equal"
        if compare_high_cards == "equal":                                              
            return [hand1, hand2]
        else:
            return [hand1] if ranks1 > ranks2 else [hand2]