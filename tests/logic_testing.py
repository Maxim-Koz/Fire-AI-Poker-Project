from poker import Card, Rank, Suit
from poker.poker_logic import showdown
from poker.players.check_player import CheckPlayer
from typing import List


def test_showdown_with_user_input():
    """
    Prompts the user to input two poker hands and runs a showdown between them.
    Hand format: "2S 3H 4D 5C 6S 7H 8D" (rank + suit, space-separated, 7 cards)
    """

    # Create two placeholder players
    player1 = CheckPlayer("Player 1", 1000, 2)
    player2 = CheckPlayer("Player 2", 1000, 2)

    # Get first hand
    print("\n=== Showdown Test ===")
    print(
        "Enter hand for Player 1 (format: RankSuit RankSuit ... - e.g., 'AS KD QH JC TS 9H 8D')"
    )
    hand1_input = input("Player 1's hand: ").strip().upper()
    hand1 = parse_hand_input(hand1_input)

    # Get second hand
    print(
        "Enter hand for Player 2 (format: RankSuit RankSuit ... - e.g., 'AS KD QH JC TS 9H 8D')"
    )
    hand2_input = input("Player 2's hand: ").strip().upper()
    hand2 = parse_hand_input(hand2_input)

    # Create hands dictionary
    hands = {player1: hand1, player2: hand2}

    # Run showdown
    print("\n--- Running Showdown ---")
    winners = showdown(hands)

    # Display results
    print("\nResults:")
    for winner, winning_hand in winners.items():
        print(f"Winner: {winner.name}")
        print(f"Winning Hand: {[str(card) for card in winning_hand]}")


def parse_hand_input(hand_string: str) -> List[Card]:
    """
    Parses a hand input string into a list of Card objects.
    Expected format: "2S 3H 4D 5C 6S 7H 8D" (7 cards, rank+suit pairs)
    """
    cards_list = []
    card_strings = hand_string.split()

    if len(card_strings) != 7 and len(card_strings) != 5:
        raise ValueError(f"Expected 7 or 5 cards, got {len(card_strings)}")

    for card_str in card_strings:
        if len(card_str) != 2:
            raise ValueError(
                f"Invalid card format: {card_str}. Expected format like 'AS', 'KD', etc."
            )

        rank_char = card_str[0]
        suit_char = card_str[1]

        # Convert character to Rank enum
        rank_map = {
            "2": Rank.TWO,
            "3": Rank.THREE,
            "4": Rank.FOUR,
            "5": Rank.FIVE,
            "6": Rank.SIX,
            "7": Rank.SEVEN,
            "8": Rank.EIGHT,
            "9": Rank.NINE,
            "T": Rank.TEN,
            "J": Rank.JACK,
            "Q": Rank.QUEEN,
            "K": Rank.KING,
            "A": Rank.ACE,
        }

        # Convert character to Suit enum
        suit_map = {
            "S": Suit.SPADES,
            "H": Suit.HEARTS,
            "D": Suit.DIAMONDS,
            "C": Suit.CLUBS,
        }

        if rank_char not in rank_map:
            raise ValueError(f"Invalid rank: {rank_char}")
        if suit_char not in suit_map:
            raise ValueError(f"Invalid suit: {suit_char}")

        rank = rank_map[rank_char]
        suit = suit_map[suit_char]
        cards_list.append(Card(rank, suit))

    return cards_list


if __name__ == "__main__":
    test_showdown_with_user_input()
