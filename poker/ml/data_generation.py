from poker.dealer import Dealer
from poker.players.random_player import RandomPlayer
from poker.hand_encoding import encode_hand  
import numpy as np

def simulate_hands(num_games=10000):
    X, y = [], []

    for _ in range(num_games):
        players = [RandomPlayer("A"), RandomPlayer("B")]
        player_money = {p: 1000 for p in players}
        dealer = Dealer(player_money, BIG_BLIND=10)

        dealer.play()
        winners = dealer.winners

        for player in dealer.player_money:
            hand_vec = encode_hand(dealer.player_cards[player], dealer.community_cards)
            X.append(hand_vec)
            y.append(1 if player in winners else 0)

    return np.array(X), np.array(y)
