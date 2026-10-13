import tensorflow as tf  # type: ignore
import numpy as np
from poker.hand_encoding import onehot_hand
from poker import Card
import logging
import logging.config
import json

with open("config/logging.json", "r") as f:
    config = json.load(f)

logging.config.dictConfig(config)

logger = logging.getLogger("hand_eval_model")


class HandEvaluator:
    def __init__(self, model_path: str):
        self.model = tf.keras.models.load_model(model_path)
        try:
            scaler_params = np.load(
                "models/scaler_params.npy", allow_pickle=True
            ).item()
            self.scaler_mean = scaler_params["mean"]
            self.scaler_scale = scaler_params["scale"]
        except FileNotFoundError:
            logger.warning("No scaler parameters found. Using raw input.")
            self.scaler_mean = None
            self.scaler_scale = None

    def predict_hand(
        self, player_hand: list[Card], community_cards: list[Card]
    ) -> float:
        hand_vec = onehot_hand(player_hand + community_cards)
        hand_vec = hand_vec.reshape(1, -1)

        if self.scaler_mean is not None and self.scaler_scale is not None:
            hand_vec = (hand_vec - self.scaler_mean) / self.scaler_scale

        prediction = self.model.predict(hand_vec)
        return float(prediction[0][0])
