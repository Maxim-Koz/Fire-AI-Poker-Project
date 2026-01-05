import tensorflow as tf   #type: ignore
from tensorflow.keras import layers, models #type: ignore
import logging
import logging.config
import json

with open('config/logging.json', 'r') as f:
    log_config = json.load(f)
logging.config.dictConfig(log_config)

logger = logging.getLogger('hand_eval_model')

def build_model() -> tf.keras.Model:
    """
    Builds a neural network to predict win probability
    given an encoded hand (hole + community cards).
    """

    logger.info("Building model...")

    model = models.Sequential([
        # Input layer expects 364 values (7 * 52 one-hot encoding)
        layers.Input(shape=(364,)),

        # Hidden layers learn non-linear relationships between cards and outcomes
        layers.Dense(256, activation='relu'),
        layers.Dense(160, activation='relu'),
        layers.Dense(128, activation='relu'),
        layers.Dense(64, activation='relu'),

        # Output layer gives a single probability between 0 and 1
        layers.Dense(1, activation='sigmoid')
    ])

    # Compile the model with optimizer, loss, and metrics
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    logger.info("Model built successfully.")

    return model
