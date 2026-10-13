"""Test module for the Player class with no name."""

from poker.dealer import Dealer
from poker.players.fake_player import FakePlayer


def test_player_with_no_name():
    """
    Attempt to initialize a dealer with two players that have no name (None).
    This should raise an error or check how the players/dealer handle invalid names.
    """
    BIG_BLIND = 2
    STARTING_MONEY = 100

    try:
        player1 = FakePlayer(None, STARTING_MONEY, BIG_BLIND)
        player2 = FakePlayer(None, STARTING_MONEY, BIG_BLIND)

        player_money = {
            player1: STARTING_MONEY,
            player2: STARTING_MONEY,
        }

        Dealer(player_money, BIG_BLIND)
        print(
            "ERROR: Dealer should not allow initialization with players that have no name"
        )
        return False
    except (AssertionError, TypeError, ValueError) as e:
        print(f"SUCCESS: Got expected error: {e}")
        return True


if __name__ == "__main__":
    test_player_with_no_name()
