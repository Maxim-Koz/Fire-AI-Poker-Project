import logging
import logging.config
import json
import random
import time
from poker import Card, Rank, Suit
from poker.ml.predict import HandEvaluator

with open("config/logging.json", "r") as f:
    config = json.load(f)

logging.config.dictConfig(config)

logger = logging.getLogger("hand_eval_model")


def test_hand_predictions():
    evaluator = HandEvaluator("models/poker_model.keras")

    ranks = [
        Rank.ACE,
        Rank.KING,
        Rank.QUEEN,
        Rank.JACK,
        Rank.TEN,
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
        Rank.SIX,
        Rank.FIVE,
        Rank.FOUR,
        Rank.THREE,
        Rank.TWO,
    ]
    suits = [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]

    num_hands = 100

    logger.info(f"Testing prediction time for {num_hands} hands using model...")

    from poker.hand_encoding import onehot_hand
    import numpy as np

    # Pre-generate all hands to exclude card creation time from timing
    hands = []
    for i in range(num_hands):
        player_cards = [
            Card(random.choice(ranks), random.choice(suits)),
            Card(random.choice(ranks), random.choice(suits)),
        ]
        community_cards = [
            Card(random.choice(ranks), random.choice(suits)),
            Card(random.choice(ranks), random.choice(suits)),
            Card(random.choice(ranks), random.choice(suits)),
            Card(random.choice(ranks), random.choice(suits)),
            Card(random.choice(ranks), random.choice(suits)),
        ]
        hands.append((player_cards, community_cards))

    # Prepare all inputs upfront
    hand_vecs = []
    for player_cards, community_cards in hands:
        hand_vec = onehot_hand(player_cards + community_cards)
        hand_vec = hand_vec.reshape(1, -1)

        if evaluator.scaler_mean is not None and evaluator.scaler_scale is not None:
            hand_vec = (hand_vec - evaluator.scaler_mean) / evaluator.scaler_scale

        hand_vecs.append(hand_vec)

    # Concatenate all inputs for batch prediction
    batch_input = np.vstack(hand_vecs)

    # Time the batch prediction
    start = time.perf_counter()
    evaluator.model.predict(batch_input, verbose=0)
    end = time.perf_counter()

    total_inference_time = (end - start) * 1000  # Convert to ms
    average_time = total_inference_time / num_hands

    if average_time > 0:
        logger.info(f"Completed {num_hands} predictions")
        logger.info(f"Total time: {total_inference_time:.4f} ms")
        logger.info(f"Average time per prediction: {average_time:.4f} ms")
        print(f"Total time: {total_inference_time:.4f} ms")
        print(f"Average time per prediction: {average_time:.4f} ms")
    else:
        logger.warning("No timing data collected")


if __name__ == "__main__":
    test_hand_predictions()
