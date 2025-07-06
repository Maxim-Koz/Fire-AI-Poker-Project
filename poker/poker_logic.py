from typing import Dict, List, Collection, Tuple
from poker.players.base_player import BasePlayer as Player
from collections import Counter
from . import Card, Suit, Rank

def showdown(hands: Dict[Player, List[Card]]) -> Dict[Player, List[Card]]: #handles showdown logic
    five_card_hands: Dict[Player, List[Card]] = {}
    player_score: Dict[Player, int] = {}
    potential_winners = {}
    winners: Dict[Player, List[Card]] = {}

    for player in hands:
        score, player_hand = evaluate_hand(hands[player])
        five_card_hands[player] = player_hand
        player_score[player] = score
    
    score_list = list(player_score.values())
    max_score = max(score_list)
    for player in player_score:
        if player_score[player] == max_score:
            potential_winners[player] = five_card_hands[player]
    
    return hands

def make_card(ranks: List[Rank], suits: List[Suit]) -> List[Card]:
    hand = []
    for id in range(5):
        hand.append(Card(ranks[id], suits[id]))
    return hand

def create_rns_list(index: List[int], ranks, suits, RANK_ORDER: Dict) -> Tuple[List[Rank], List[Suit]]: #creates ranks and suit list
    REVERSE_RANK_ORDER = {id: rank for rank, id in RANK_ORDER.items()}
    rank_cards = []
    suit_cards = []
    for card_index in index:
        rank_cards.append(REVERSE_RANK_ORDER[ranks(card_index)])
        suit_cards.append(suits[card_index])
    return rank_cards, suit_cards

def final_hand(index: List[int], ranks, suits, RANK_ORDER: Dict):
    rank_cards, suit_cards = create_rns_list(index, ranks, suits, RANK_ORDER)
    player_hand = make_card(rank_cards, suit_cards)
    return player_hand

def parse_hand(hand: Collection[Card]) -> Tuple[Dict, List[int], List[Suit]]:
        RANK_ORDER = {rank: i for i, rank in enumerate(Rank, start=2)}  # mapping ranks to their order, starting from 2
        sorted_hand = sorted(hand, key=lambda card: RANK_ORDER[card.rank], reverse=True)#sort hand by rank
        ranks = [RANK_ORDER[card.rank] for card in sorted_hand]
        suits = [card.suit for card in sorted_hand] 
        return RANK_ORDER, ranks, suits 
    
def is_straight(ranks: List[int]) -> Tuple[bool, List[int]]: 
    for i in range(3):
        potential_straight = ranks[i:i+5] 
        dif = 0
        for k in range(4):
            if potential_straight[k] == potential_straight[k+1] + 1:
                dif += 1
        if dif == 4:
            indexed_hand = [x+i for x in range(5)]
            return True, indexed_hand
    if ranks[0] == 14 and ranks[3:] == [5, 4, 3, 2, 1]:
        return True, [0, 3, 4, 5, 6]
    return False, [0]

def is_flush(suits: List[Suit]) -> Tuple[bool, List[int]]:
    indexed_hand = []
    suit_counter = Counter(suits)
    if suit_counter.most_common(1)[0][1] == 5:
        for suit_index in range(len(suits)):
            if suit_index == suit_counter.most_common(1)[0][0]:
                indexed_hand.append(suit_index)
        return True, indexed_hand
    return False, [0]

def is_four_of_a_kind(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]: 
    most_common_rank = rank_counter.most_common(1)[0][0]

    if rank_counter.most_common(1)[0][1] == 4:
        _flag = 0
        cards = []
        for i in range(len(ranks)):
            if ranks[i] == most_common_rank:
                cards.append(i)
            elif _flag == 0:
                cards.append(i)
                _flag += 1
        return True, cards
    return False, [0]


def is_full_house(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:  
    if rank_counter.most_common(1)[0][1] == 3:
        cards = []
        most_common_rank = rank_counter.most_common(1)[0][0]
        if rank_counter.most_common(2)[1][1] == 2:
            if len(rank_counter) == 4:
                for i in range(len(ranks)):
                    if ranks[i] == most_common_rank or ranks[i] == rank_counter.most_common(1)[1][0]:
                        cards.append(i)
                return True, cards
            else:
                rank1 = list(rank_counter)[1]
                rank2 = list(rank_counter)[2]
                if rank1 > rank2:
                    for i in range(len(ranks)):
                        if ranks[i] == most_common_rank or ranks[i] == rank1:
                            cards.append(i)
                    return True, cards
                else:
                    for i in range(len(ranks)):
                        if ranks[i] == most_common_rank or ranks[i] == rank2:
                            cards.append(i)
                    return True, cards
        elif len(rank_counter) == 3:
            count = 0
            rank1 = list(rank_counter)[0]
            rank2 = list(rank_counter)[1]
            if rank1 > rank2:
                for i in range(len(ranks)):
                    if ranks[i] == rank1:
                        cards.append(i)
                    elif ranks[i] == rank2 and count <= 1:
                        count += 1
                        cards.append(i)
                return True, cards
            else:
                for i in range(len(ranks)):
                    if ranks[i] == rank2:
                        cards.append(i)
                    elif ranks[i] == rank1 and count <= 1:
                        count += 1
                        cards.append(i)
                return True, cards
    return False, [0]
    

def is_three_of_a_kind(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:
    if rank_counter.most_common(1)[0][1] == 3:
        cards = []
        _flag = 0
        for i in range(len(ranks)):
            if i == rank_counter.most_common(1)[0][0]:
                cards.append(i)
            elif _flag <= 1:
                cards.append(i)
        return True, cards
    return False, [0]

def is_two_pair(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:
    if len(rank_counter) == 5:
        cards = []
        count = 0
        rank1 = list(rank_counter)[0]
        rank2 = list(rank_counter)[1]
        for i in range(len(ranks)):
            if ranks[i] == rank1 or ranks[i] == rank2:
                cards.append(i)
            elif count == 0:
                cards.append(i)
        return True, cards
    return False, [0]


def is_one_pair(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:
    if rank_counter.most_common(1)[0][1] == 2:
        counter = 0
        cards = []
        for i in range(len(ranks)):
            if ranks[1] == rank_counter.most_common(1)[0][0]:
                cards.append(i)
            elif counter <= 2:
                cards.append(i)
        return True, cards
    return False, [0]


def evaluate_hand( hand: List[Card]) -> Tuple[int, List[Card]]:  
    #gives value based on hand rating, higher is better

    RANK_ORDER, ranks, suits = parse_hand(hand)
    rank_counter = Counter(ranks)

    is_it_flush, indexed_flush = is_flush(suits)
    is_it_straight, indexed_straight = is_straight(ranks)
    if is_it_flush and is_it_straight and indexed_flush == indexed_straight: #straight flush 
        return 8, final_hand(indexed_straight, ranks, suits, RANK_ORDER)
    
    is_it_foak, indexed_foak = is_four_of_a_kind(ranks, rank_counter)
    if is_it_foak: # four of a kind 
        return 7, final_hand(indexed_foak, ranks, suits, RANK_ORDER)
    
    is_it_full_house, indexed_full_house = is_full_house(ranks, rank_counter)
    if is_it_full_house: # full house
        return 6, final_hand(indexed_full_house, ranks, suits, RANK_ORDER)
    
    if is_it_flush: # flush 
        return 5, final_hand(indexed_flush, ranks, suits, RANK_ORDER)
    
    if is_it_straight: # straight 
        return 4, final_hand(indexed_straight, ranks, suits, RANK_ORDER)
    
    is_it_toak, indexed_toak = is_three_of_a_kind(ranks, rank_counter)
    if is_it_toak: # three of a kind 
        return 3, final_hand(indexed_toak, ranks, suits, RANK_ORDER)
    
    is_it_two_pair, indexed_two_pair = is_two_pair(ranks, rank_counter)
    if is_it_two_pair: # two pair 
        return 2, final_hand(indexed_two_pair, ranks, suits, RANK_ORDER)
    
    is_it_one_pair, indexed_one_pair = is_one_pair(ranks, rank_counter)
    if is_it_one_pair: # one pair 
        return 1, final_hand(indexed_one_pair, ranks, suits, RANK_ORDER)
    
    #high card
    return 0, final_hand([0,1,2,3,4], ranks, suits, RANK_ORDER)


def tie_breaker(hand1: List[Card], hand2: List[Card]) -> List[List[Card]]:
    _, ranks1, _ = parse_hand(hand1)
    _, ranks2, _= parse_hand(hand2)
    if ranks1 > ranks2:
        return [hand1]
    elif ranks2 > ranks1:
        return [hand2]
    else:
        return [hand1, hand2]