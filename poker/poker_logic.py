from typing import Dict, List, Tuple
from poker.players.base_player import BasePlayer as Player
from collections import Counter
from . import Card, Suit, Rank
from .hand_encoding import parse_hand
import logging
import logging.config
import json

with open("config/logging.json", "r") as f:
    config = json.load(f)

logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def showdown(hands: Dict[Player, List[Card]]) -> Dict[Player, List[Card]]:
    logger.info("starting showdown")

    # Check for valid cards and duplicate cards in all hands
    for player in hands:
        # Check that all cards are valid Card instances
        for card in hands[player]:
            if not isinstance(card, Card):
                raise ValueError(f"Invalid card type in {player}'s hand: {card}")
            if not isinstance(card.rank, Rank):
                raise ValueError(f"Invalid rank in {player}'s hand: {card.rank}")
            if not isinstance(card.suit, Suit):
                raise ValueError(f"Invalid suit in {player}'s hand: {card.suit}")

        # Check for duplicate cards in all hands
        if len(hands[player]) != len(set(hands[player])):
            raise ValueError(f"Duplicate cards found in {player}'s hand")

    five_card_hands: Dict[Player, List[Card]] = {}
    player_score: Dict[Player, int] = {}
    potential_winners = []
    winners: Dict[Player, List[Card]] = {}

    for player in hands:
        score, player_hand = evaluate_hand(hands[player])
        five_card_hands[player] = player_hand
        player_score[player] = score

    score_list = list(player_score.values())
    max_score = max(score_list)
    for player in player_score:
        if player_score[player] == max_score:
            potential_winners.append(player)
    for player in potential_winners:
        if len(winners) == 0:
            winners[player] = five_card_hands[player]
        else:
            first_hand = next(iter(winners.values()))
            winner = tie_breaker(five_card_hands[player], first_hand, max_score)
            if [five_card_hands[player]] == winner:
                winners = {player: five_card_hands[player]}
            elif [five_card_hands[player], first_hand] == winner:
                winners[player] = five_card_hands[player]
    return winners


def make_card(
    ranks: List[Rank], suits: List[Suit]
) -> List[Card]:  # creates a list of 5 cards from ranks and suits
    hand = []
    for id in range(5):
        hand.append(Card(ranks[id], suits[id]))
    return hand


def create_rns_list(
    index, ranks, suits, RANK_ORDER: Dict
) -> Tuple[List[Rank], List[Suit]]:  # creates list of ranks and suit
    REVERSE_RANK_ORDER = {id: rank for rank, id in RANK_ORDER.items()}
    rank_cards = []
    suit_cards = []
    for card_index in index:
        rank_cards.append(REVERSE_RANK_ORDER[ranks[card_index]])
        suit_cards.append(suits[card_index])
    return rank_cards, suit_cards


def final_hand(index: List[int], ranks, suits, RANK_ORDER: Dict):
    rank_cards, suit_cards = create_rns_list(index, ranks, suits, RANK_ORDER)
    player_hand = make_card(rank_cards, suit_cards)
    return player_hand


def is_straight_flush(ranks: List[int], suits: List[Suit]) -> Tuple[bool, List[int]]:
    is_it_straight, id_straight = is_straight(ranks)
    is_it_flush, id_flush = is_flush(suits)
    if not is_it_straight or not is_it_flush:
        return False, [0]
    if id_flush == id_straight:
        logger.info("straight flush")
        return True, id_flush

    unique_ranks = list(dict.fromkeys(ranks))  # finds all unique ranks, in order
    all_possible_straights = []
    all_possible_flushes = []

    # finds all possible straights
    num_iterations = len(unique_ranks) - 4
    for i in range(num_iterations):
        potential_straight = unique_ranks[i : i + 5]
        dif = 0
        indexed_hand = []
        for k in range(4):
            if potential_straight[k] == potential_straight[k + 1] + 1:
                dif += 1
        if dif == 4:
            for rank in potential_straight:
                for rank_id in range(len(ranks)):
                    if ranks[rank_id] == rank:
                        indexed_hand.append(rank_id)
                        break
            all_possible_straights.append(
                indexed_hand
            )  # this all the possible straights from best to worst

    # finds all possible flushes
    suits_counter = Counter(suits)
    for suit in suits_counter:
        if suits_counter[suit] >= 5:
            indexed_hand = []
            for suit_id in range(7):  # 7 is the len(suit)
                indexed_hand.append(suit_id)
            all_possible_flushes.append(indexed_hand)

    for straight_id in all_possible_straights:
        for flush_id in all_possible_flushes:
            if (
                straight_id == flush_id
            ):  # if straight and flush have the same index, we have a straight flush
                logger.info("straight flush")
                return True, straight_id
    return False, [0]


def is_straight(ranks: List[int]) -> Tuple[bool, List[int]]:
    unique_ranks = list(dict.fromkeys(ranks))  # finds all unique ranks, in order
    if len(unique_ranks) >= 5:
        indexed_hand = []
        num_iterations = len(unique_ranks) - 4
        for i in range(num_iterations):
            potential_straight = unique_ranks[i : i + 5]
            dif = 0
            for k in range(4):
                if potential_straight[k] == potential_straight[k + 1] + 1:
                    dif += 1
            if dif == 4:
                for rank in potential_straight:
                    for rank_id in range(len(ranks)):
                        if ranks[rank_id] == rank:
                            indexed_hand.append(rank_id)
                            break
                logger.info("straight")
                return True, indexed_hand
        wheel = [14, 2, 3, 4, 5]
        if set(wheel).issubset(ranks):
            for rank_id in range(len(ranks)):
                for rank in wheel:
                    if ranks[rank_id] == rank:
                        indexed_hand.append(rank_id)
                        break
            logger.info("straight")
            return True, indexed_hand
    return False, [0]


def is_flush(suits: List[Suit]) -> Tuple[bool, List[int]]:
    indexed_hand = []
    suit_counter = Counter(suits)
    if suit_counter.most_common(1)[0][1] >= 5:
        count = 0
        for suit_index in range(len(suits)):
            if suits[suit_index] == suit_counter.most_common(1)[0][0] and count < 5:
                count += 1
                indexed_hand.append(suit_index)
        logger.info("flush")
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
        logger.info("foak")
        return True, cards
    return False, [0]


def is_full_house(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:
    trips = [rank for rank, count in rank_counter.items() if count >= 3]
    pairs = [rank for rank, count in rank_counter.items() if count >= 2]

    if not trips or len(pairs) < 2 and (len(trips) == 1 and trips[0] not in pairs):
        return False, [0]

    trips.sort(reverse=True)
    pairs.sort(reverse=True)

    # Choose best triplet
    trip_rank = trips[0]

    if trip_rank in pairs:
        pairs.remove(trip_rank)

    if not pairs:
        return False, [0]

    pair_rank = pairs[0]

    # Collect indices of full house
    cards = []
    trip_count = 0
    pair_count = 0

    for i, rank in enumerate(ranks):
        if rank == trip_rank and trip_count < 3:
            cards.append(i)
            trip_count += 1
        elif rank == pair_rank and pair_count < 2:
            cards.append(i)
            pair_count += 1
        if len(cards) == 5:
            break

    logger.info("full house")
    return True, cards


def is_three_of_a_kind(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:
    if rank_counter.most_common(1)[0][1] == 3:
        cards = []
        _flag = 0
        for i in range(len(ranks)):
            if ranks[i] == rank_counter.most_common(1)[0][0]:
                cards.append(i)
            elif _flag <= 1:
                cards.append(i)
        logger.info("toak")
        return True, cards
    return False, [0]


def is_two_pair(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:
    pairs = [rank for rank, count in rank_counter.items() if count == 2]
    if len(pairs) == 2:
        cards = []
        count = 0
        for i in range(len(ranks)):
            if ranks[i] == pairs[0] or ranks[i] == pairs[1]:
                cards.append(i)
            elif count == 0:
                count += 1
                cards.append(i)
        logger.info("two pair")
        return True, cards
    return False, [0]


def is_one_pair(ranks: List[int], rank_counter) -> Tuple[bool, List[int]]:
    if rank_counter.most_common(1)[0][1] == 2:
        counter = 0
        cards = []
        for i in range(len(ranks)):
            if ranks[i] == rank_counter.most_common(1)[0][0]:
                cards.append(i)
            elif counter <= 2:
                counter += 1
                cards.append(i)
        logger.info("one pair")
        return True, cards
    return False, [0]


def evaluate_hand(hand: List[Card]) -> Tuple[int, List[Card]]:
    # gives value based on hand rating, higher is better

    RANK_ORDER, ranks, suits = parse_hand(hand)
    rank_counter = Counter(ranks)

    is_it_flush, indexed_flush = is_flush(suits)
    is_it_straight, indexed_straight = is_straight(ranks)
    is_it_straight_flush, indexed_straight_flush = is_straight_flush(ranks, suits)
    if is_it_straight_flush:
        return 8, final_hand(indexed_straight_flush, ranks, suits, RANK_ORDER)

    is_it_foak, indexed_foak = is_four_of_a_kind(ranks, rank_counter)
    if is_it_foak:
        return 7, final_hand(indexed_foak, ranks, suits, RANK_ORDER)

    is_it_full_house, indexed_full_house = is_full_house(ranks, rank_counter)
    if is_it_full_house:
        return 6, final_hand(indexed_full_house, ranks, suits, RANK_ORDER)

    if is_it_flush:
        return 5, final_hand(indexed_flush, ranks, suits, RANK_ORDER)

    if is_it_straight:
        return 4, final_hand(indexed_straight, ranks, suits, RANK_ORDER)

    is_it_toak, indexed_toak = is_three_of_a_kind(ranks, rank_counter)
    if is_it_toak:
        return 3, final_hand(indexed_toak, ranks, suits, RANK_ORDER)

    is_it_two_pair, indexed_two_pair = is_two_pair(ranks, rank_counter)
    if is_it_two_pair:
        return 2, final_hand(indexed_two_pair, ranks, suits, RANK_ORDER)

    is_it_one_pair, indexed_one_pair = is_one_pair(ranks, rank_counter)
    if is_it_one_pair:
        return 1, final_hand(indexed_one_pair, ranks, suits, RANK_ORDER)
    logger.info("high card")
    return 0, final_hand([0, 1, 2, 3, 4], ranks, suits, RANK_ORDER)


def tie_breaker(hand1: List[Card], hand2: List[Card], score: int) -> List[List[Card]]:
    logger.info("starting tie break")
    _, ranks1, _ = parse_hand(hand1)
    _, ranks2, _ = parse_hand(hand2)
    ranks1_counter = Counter(ranks1)
    ranks2_counter = Counter(ranks2)
    if score == 8:  # straight flush
        if ranks1 > ranks2:
            return [hand1]
        elif ranks2 > ranks1:
            return [hand2]
    elif score == 7:  # four of a kind
        quad1 = ranks1_counter.most_common(1)[0][0]
        kicker1 = ranks1_counter.most_common(2)[1][0]
        quad2 = ranks2_counter.most_common(1)[0][0]
        kicker2 = ranks2_counter.most_common(2)[1][0]
        if quad1 > quad2:
            return [hand1]
        elif quad2 > quad1:
            return [hand2]
        elif kicker1 > kicker2:
            return [hand1]
        elif kicker2 > kicker1:
            return [hand2]
    elif score == 6:  # full house
        trips1 = ranks1_counter.most_common(1)[0][0]
        pair1 = ranks1_counter.most_common(2)[1][0]
        trips2 = ranks2_counter.most_common(1)[0][0]
        pair2 = ranks2_counter.most_common(2)[1][0]
        if trips1 > trips2:
            return [hand1]
        elif trips2 > trips1:
            return [hand2]
        elif pair1 > pair2:
            return [hand1]
        elif pair2 > pair1:
            return [hand2]
    elif score == 5:  # flush
        if ranks1 > ranks2:
            return [hand1]
        elif ranks2 > ranks1:
            return [hand2]
    elif score == 4:  # straight
        if ranks1 > ranks2:
            return [hand1]
        elif ranks2 > ranks1:
            return [hand2]
    elif score == 3:  # three of a kind
        trip1 = ranks1_counter.most_common(1)[0][0]
        kickers1 = [rank for rank, count in ranks1_counter.items() if count < 3]
        kickers1 = sorted(kickers1, reverse=True)
        trip2 = ranks2_counter.most_common(1)[0][0]
        kickers2 = [rank for rank, count in ranks2_counter.items() if count < 3]
        kickers2 = sorted(kickers2, reverse=True)
        if trip1 > trip2:
            return [hand1]
        elif trip2 > trip1:
            return [hand2]
        elif kickers1 > kickers2:
            return [hand1]
        elif kickers2 > kickers1:
            return [hand2]
    elif score == 2:  # two pair
        pairs1 = [rank for rank, count in ranks1_counter.items() if count == 2]
        pairs1 = sorted(pairs1, reverse=True)
        kicker1 = ranks1_counter.most_common(2)[1][0]
        pairs2 = [rank for rank, count in ranks2_counter.items() if count == 2]
        pairs2 = sorted(pairs2, reverse=True)
        kicker2 = ranks2_counter.most_common(2)[1][0]
        if pairs1 > pairs2:
            return [hand1]
        elif pairs2 > pairs1:
            return [hand2]
        elif kicker1 > kicker2:
            return [hand1]
        elif kicker2 > kicker1:
            return [hand2]
    elif score == 1:  # one pair
        pair1 = ranks1_counter.most_common(1)[0][0]
        kickers1 = [rank for rank, count in ranks1_counter.items() if count == 1]
        kickers1 = sorted(kickers1, reverse=True)
        pair2 = ranks2_counter.most_common(1)[0][0]
        kickers2 = [rank for rank, count in ranks2_counter.items() if count == 1]
        kickers2 = sorted(kickers2, reverse=True)
        if pair1 > pair2:
            return [hand1]
        elif pair2 > pair1:
            return [hand2]
        elif kickers1 > kickers2:
            return [hand1]
        elif kickers2 > kickers1:
            return [hand2]
    if ranks1 > ranks2:
        return [hand1]
    elif ranks2 > ranks1:
        return [hand2]
    return [hand1, hand2]
