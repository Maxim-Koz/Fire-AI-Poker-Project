import numpy as np
from sklearn.model_selection import train_test_split #type: ignore
from sklearn.preprocessing import StandardScaler #type: ignore
from sklearn.metrics import classification_report #type: ignore
import logging
import logging.config
import json
from .hand_eval_model import build_model
from .data_generation import simulate_hands

with open("config/logging.json") as f:
    log_config = json.load(f)
logging.config.dictConfig(log_config)

logger = logging.getLogger('hand_eval_model')

def main():
    logger.info("Starting poker model training...")

    # Generate or load training data
    X, y = simulate_hands()
    logger.info(f"Loaded {len(X)} samples")

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = build_model()
    logger.info("Model built successfully")

    # Train the model
    history = model.fit(
        X_train_scaled, y_train,
        epochs=20,
        batch_size=64,
        validation_data=(X_test_scaled, y_test),
        verbose=1
    )

    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    y_pred_classes = (y_pred > 0.5).astype(int)
    
    logger.info("\nModel Performance Report:")
    logger.info("\n" + classification_report(y_test, y_pred_classes))

    # Save both model and scaler
    model.save("models/poker_model.h5")
    np.save("models/scaler_params.npy", 
            {"mean": scaler.mean_, "scale": scaler.scale_})
    logger.info("Model and scaler parameters saved successfully")

if __name__ == "__main__":
    main()
