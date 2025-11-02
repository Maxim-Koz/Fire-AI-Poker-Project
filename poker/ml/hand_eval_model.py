import tensorflow as tf   #type: ignore
from tensorflow.keras import layers, models  #type: ignore
import numpy as np
from poker import Card, Rank, Suit

# Define model
model = models.Sequential([
    layers.Input(shape=(364,)),            # input vector (hole + community)
    layers.Dense(256, activation='relu'),
    layers.Dense(128, activation='relu'),
    layers.Dense(64, activation='relu'),
    layers.Dense(1, activation='sigmoid')  # output: win probability
])

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

def card_to_index(card: Card) -> int:
    # Define ordering for ranks and suits
    ranks = [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN,
             Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]
    suits = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]

    rank_index = ranks.index(card.rank)   # 0-12
    suit_index = suits.index(card.suit)   # 0-3

    return rank_index * 4 + suit_index


def encode_hand(hole_cards: list[Card], board_cards: list[Card]) -> np.ndarray:
    num_slots = 7
    vec = np.zeros(num_slots * 52)

    all_cards = hole_cards + board_cards
    for i, card in enumerate(all_cards):
        idx = card_to_index(card)
        slot_start = i * 52
        vec[slot_start + idx] = 1.0

    return vec
