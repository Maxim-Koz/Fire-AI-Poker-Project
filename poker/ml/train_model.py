import os
import numpy as np
from sklearn.model_selection import GroupKFold #type: ignore
from sklearn.preprocessing import StandardScaler #type: ignore
from sklearn.metrics import classification_report #type: ignore 
import logging
import logging.config
import json
from .hand_eval_model import build_model
import math
import tensorflow as tf  # type: ignore
from typing import Iterator, Tuple
from sklearn.utils.class_weight import compute_class_weight  # add this import

with open("config/logging.json") as f:
    log_config = json.load(f)
logging.config.dictConfig(log_config)

logger = logging.getLogger('hand_eval_model')



def open_memmap_checked(path: str, dtype, shape, create_if_missing=False):
    # shape may be (None, dim1, dim2) to auto-infer first axis from file size
    if shape[0] is None:
        # compute size for one item on remaining dims
        per_item_bytes = int(np.prod(shape[1:])) * np.dtype(dtype).itemsize
        if not os.path.exists(path):
            if create_if_missing:
                raise RuntimeError("Cannot create memmap with unknown first dimension.")
            raise FileNotFoundError(f"{path} not found. Please generate the memmap first.")
        total_bytes = os.path.getsize(path)
        if total_bytes % per_item_bytes != 0:
            raise IOError(f"{path} size {total_bytes} not divisible by per-item bytes {per_item_bytes}.")
        first = total_bytes // per_item_bytes
        shape = (int(first),) + tuple(shape[1:])
    expected = int(np.prod(shape)) * np.dtype(dtype).itemsize
    if not os.path.exists(path):
        if create_if_missing:
            mmap = np.memmap(path, dtype=dtype, mode="w+", shape=shape)
            mmap.flush()
            return mmap
        raise FileNotFoundError(f"{path} not found. Please generate the memmap with shape={shape}")
    size = os.path.getsize(path)
    if size < expected:
        raise IOError(f"{path} is too small ({size} bytes) for expected shape {shape} ({expected} bytes). Regenerate with matching shape.")
    if size > expected:
        raise IOError(f"{path} is larger ({size} bytes) than expected for shape {shape} ({expected} bytes). Check dtype/shape.")
    return np.memmap(path, dtype=dtype, mode="r", shape=shape)

# Use None as first axis to auto-detect number of games
game_cards = open_memmap_checked("game_cards.dat", np.float32, (None, 2, 364))
winners    = open_memmap_checked("winners.dat",    np.int64,   (None, 2))
# logger.info(f"Loaded memmapped training data from disk (shape: {game_cards.shape}).")

# Create game indices to keep track of which hands belong to which game
game_indices = np.repeat(np.arange(game_cards.shape[0]), 2)

# Reshape the data (views of memmap, do NOT copy)
X_mm = game_cards.reshape(-1, game_cards.shape[-1])  # memmap view, dtype=float32
y_mm = winners.reshape(-1)  # memmap view, dtype=int64

logger.info(f"Loaded {len(X_mm)} samples from {game_cards.shape[0]} games")

# Use GroupKFold to ensure hands from the same game stay together
group_kfold = GroupKFold(n_splits=5)
train_idx, test_idx = next(group_kfold.split(X_mm, y_mm, groups=game_indices))
logger.info(f"Train samples: {len(train_idx)}, Val samples: {len(test_idx)}")

# ----- streaming/incremental processing only (no in-memory fit_transform) -----
# Incremental scaling: compute mean/var with partial_fit over mini-batches
scaler = StandardScaler()
batch_size = 4096  # lower if you still hit memory issues
for start in range(0, len(train_idx), batch_size):
    batch_idx = train_idx[start : start + batch_size]
    Xb = X_mm[batch_idx].astype(np.float32, copy=False)
    scaler.partial_fit(Xb)
logger.info("Scaler fitted incrementally.")

# build tf.data.Dataset generator (keeps memmap on disk)
def dataset_from_indices(
    X_mem: np.ndarray,
    y_mem: np.ndarray,
    indices: np.ndarray,
    batch_size: int,
    shuffle: bool = True,
) -> tf.data.Dataset:
    def gen():
        idxs = indices.copy()
        if shuffle:
            np.random.shuffle(idxs)
        for i in range(0, len(idxs), batch_size):
            batch_idx = idxs[i : i + batch_size]
            Xb = X_mem[batch_idx].astype(np.float32, copy=False)
            Xb = (Xb - scaler.mean_) / scaler.scale_
            yb = y_mem[batch_idx].astype(np.int64, copy=False)
            yield Xb, yb

    out_sig = (
        tf.TensorSpec(shape=(None, X_mem.shape[1]), dtype=tf.float32),
        tf.TensorSpec(shape=(None,), dtype=tf.int64),
    )

    ds = tf.data.Dataset.from_generator(lambda: gen(), output_signature=out_sig)
    ds = ds.prefetch(tf.data.AUTOTUNE)

    # make training dataset repeat forever so Keras doesn't run out of data
    if shuffle:
        ds = ds.repeat()

    return ds

# create datasets (no sample weights from generator)
train_ds = dataset_from_indices(X_mm, y_mm, train_idx, batch_size, shuffle=True)
val_ds   = dataset_from_indices(X_mm, y_mm, test_idx,  batch_size, shuffle=False)

steps_per_epoch = math.ceil(len(train_idx) / batch_size)
validation_steps = math.ceil(len(test_idx) / batch_size)

# compute balanced class weights from training labels and pass to model.fit
train_labels = y_mm[train_idx].astype(int)
classes = np.unique(train_labels)
cw_vals = compute_class_weight("balanced", classes=classes, y=train_labels)
class_weight = {int(c): float(w) for c, w in zip(classes, cw_vals)}
logger.info(f"Using class_weight: {class_weight}")

# log label distributions
logger.info(f"Train label distribution: {dict(zip(*np.unique(train_labels, return_counts=True)))}")
val_labels = y_mm[test_idx].astype(int)
logger.info(f"Val label distribution:   {dict(zip(*np.unique(val_labels, return_counts=True)))}")

# ensure models dir exists
os.makedirs("models", exist_ok=True)

model = build_model()
# save model summary to file
with open("models/model_summary.txt", "w") as fh:
    model.summary(print_fn=lambda s: fh.write(s + "\n"))

# make val_ds finite for validation
val_ds_finite = val_ds.take(validation_steps)

# add useful callbacks: early stopping and LR reduction
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-7),
]

history = model.fit(
    train_ds,
    epochs=20,
    steps_per_epoch=steps_per_epoch,
    validation_data=val_ds_finite,
    validation_steps=validation_steps,
    class_weight=class_weight,
    callbacks=callbacks,
    verbose=1,
)

# safer evaluation: predict on the finite validation dataset and compare to true labels
val_preds = model.predict(val_ds.take(validation_steps), steps=validation_steps, verbose=1).reshape(-1)
y_true = y_mm[test_idx].astype(int)
n = min(len(y_true), len(val_preds))
y_true = y_true[:n]
val_preds = val_preds[:n]
y_pred_classes = (val_preds > 0.5).astype(int)

from sklearn.metrics import confusion_matrix, roc_auc_score, precision_recall_curve
logger.info(f"Confusion matrix:\n{confusion_matrix(y_true, y_pred_classes)}")
try:
    auc = roc_auc_score(y_true, val_preds)
    logger.info(f"Validation ROC AUC: {auc:.4f}")
except Exception:
    logger.warning("ROC AUC could not be computed.")

# find best threshold by maximizing F1 on val set
prec, rec, thr = precision_recall_curve(y_true, val_preds)
f1 = 2 * prec * rec / (prec + rec + 1e-12)
# thr has length len(prec)-1, align carefully
if len(f1) > 0:
    best_i = int(np.nanargmax(f1))
    # If thr length matches, pick threshold safely
    if best_i < len(thr):
        best_threshold = float(thr[best_i])
    else:
        best_threshold = 0.5
    best_f1 = float(np.nanmax(f1))
    logger.info(f"Best threshold by F1: {best_threshold:.4f}, F1: {best_f1:.4f}")
    # persist threshold for inference
    np.save("models/best_threshold.npy", np.array(best_threshold, dtype=np.float32))
else:
    logger.info("Could not compute a best threshold (empty precision-recall curve).")

logger.info("\nModel Performance Report:")
logger.info("\n" + classification_report(y_true, y_pred_classes))

# Save model and scaler params
model.save("models/poker_model.keras")
np.save("models/scaler_params.npy", {"mean": scaler.mean_, "scale": scaler.scale_})
logger.info("Model and scaler parameters saved successfully")

