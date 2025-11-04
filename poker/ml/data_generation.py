from poker.dealer import Dealer
from poker.players.check_player import CheckPlayer
from poker.hand_encoding import onehot_hand 
import numpy as np
import logging
import logging.config
import json

with open('config/logging.json', 'r') as f:
    log_config = json.load(f)
logging.config.dictConfig(log_config)

logger = logging.getLogger('hand_eval_model')

def simulate_hands(num_games=10000):
    logger.info(f"Starting simulation of {num_games} hands.")
    X, y = [], []

    for game_number in range(num_games):
        players = [RandomPlayer("A"), RandomPlayer("B")]
        player_money = {p: 1000 for p in players}
        dealer = Dealer(player_money, BIG_BLIND=10)

        logger.info(f"Game number {game_number}")
        dealer.play()
        winners = dealer.winners

        for player in dealer.player_money:
            hand_vec = onehot_hand(dealer.player_cards[player] + dealer.community_cards)
            X.append(hand_vec)
            y.append(1 if player in winners else 0)

    return np.array(X), np.array(y)