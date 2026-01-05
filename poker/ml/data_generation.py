from poker import deck as random_deck
from poker import Card
from poker.players.check_player import BasePlayer, CheckPlayer
from poker.poker_logic import showdown
from poker.hand_encoding import onehot_hand 
from typing import Final
import numpy as np
import random
import logging
import logging.config
import json

with open('config/logging.json', 'r') as f:
    log_config = json.load(f)
logging.config.dictConfig(log_config)

logger = logging.getLogger('hand_eval_model')

def simulate_hand() -> tuple[np.ndarray, np.ndarray]:
    players: list[BasePlayer] = [CheckPlayer("A", 1000, 10), CheckPlayer("B", 1000, 10)]
    players_hands: dict[BasePlayer, list[Card]] = {player: [] for player in players}
    final_hands = []
    deck = random_deck()
    for player in players: #? Two players for now
        player_cards = [deck.pop(0), deck.pop(0)]
        players_hands[player].extend(player_cards) #Dealing cards

    extra_cards = random.randint(0,5)
    for _ in range(extra_cards):
        card = deck.pop(0)
        for player in players: 
            players_hands[player].append(card)

    for hand in players_hands.values():
        hand_vec = onehot_hand(hand)
        final_hands.append(hand_vec)

    final_cards = 5-extra_cards  #dealing remaining community cards
    for _ in range(final_cards):
        card = deck.pop(0)
        for player in players:
            players_hands[player].append(card)
    
    winning_players = showdown(players_hands)
    winners = []
    for player in players:
        if player in winning_players:
            winners.append(1)
        else:
            winners.append(0)
    return np.array(final_hands), np.array(winners)


def generate_chunk(num_games: int) -> tuple[np.ndarray, np.ndarray]:
    # this function will generate a number of games each time it is run
    # which is usefull as less RAM is used at any one time

    logger.info(f"Generating chunk of {num_games} games.")
    game_cards, winners = [], []

    for _ in range(num_games):
        hands, winner = simulate_hand()
        game_cards.append(hands)
        winners.append(winner)
    return np.array(game_cards), np.array(winners)

HAND_VEC_SIZE: Final = 364  
TOTAL_GAMES: Final = 1_000_000
CHUNK_SIZE: Final = 10000  

#use memmap to handle large data in chuncks
#which is better than something like .save()
games_mm = np.memmap(
    "game_cards.dat",
    dtype=np.float32,
    mode="w+",
    shape=(TOTAL_GAMES, 2, HAND_VEC_SIZE)
)

winners_mm = np.memmap(
    "winners.dat",
    dtype=np.int64,
    mode="w+",
    shape=(TOTAL_GAMES, 2)
    )

write_index = 0

while write_index < TOTAL_GAMES:
    batch_size = min(CHUNK_SIZE, TOTAL_GAMES - write_index)

    cards_batch = np.zeros((batch_size, 2, HAND_VEC_SIZE), dtype=np.float32)
    winners_batch = np.zeros((batch_size, 2), dtype=np.int64)

    # simulate batch
    for i in range(batch_size):
        cards, win = simulate_hand()
        cards_batch[i] = cards
        winners_batch[i] = win

    # write to memmap
    games_mm[write_index:write_index+batch_size] = cards_batch
    winners_mm[write_index:write_index+batch_size] = winners_batch

    # flush to disk
    games_mm.flush()
    winners_mm.flush()

    write_index += batch_size
    logger.info(f"Wrote {write_index}/{TOTAL_GAMES} games to disk.")

logger.info("Data generation complete.")





        



