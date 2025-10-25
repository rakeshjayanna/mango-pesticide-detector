"""
CNN trainer for Mango Pesticide Detection using TensorFlow/Keras.

Expects a dataset folder with two subfolders:
  dataset/
    ├── pesticide/
    └── organic/

This script will:
- Load and split the dataset into training and validation sets
- Apply on-the-fly data augmentation
- Build a small CNN model
- Train with early stopping and checkpointing
- Save the best model as `mango_model.h5` in this directory
- Plot and save training curves to `training_curves.png`
- Save label mapping to `class_indices.json`

Usage (from repo root or from server/model):
  python server/model/model_trainer.py --data-dir ./dataset --epochs 15 --img-size 224 224 --batch-size 32
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
import tensorflow as tf


THIS_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET_DIR = (THIS_DIR.parent.parent / 'dataset').resolve()
DEFAULT_OUTPUT_MODEL = (THIS_DIR / 'mango_model.h5').resolve()
DEFAULT_HISTORY_JSON = (THIS_DIR / 'history.json').resolve()
DEFAULT_TRAINING_PLOT = (THIS_DIR / 'training_curves.png').resolve()
DEFAULT_LABELS_JSON = (THIS_DIR / 'class_indices.json').resolve()


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train a CNN to classify mango images as pesticide or organic.")
    p.add_argument('--data-dir', type=Path, default=DEFAULT_DATASET_DIR, help='Path to dataset directory containing class subfolders')
    p.add_argument('--epochs', type=int, default=15, help='Number of training epochs')
    p.add_argument('--batch-size', type=int, default=32, help='Batch size')
    p.add_argument('--img-size', type=int, nargs=2, default=[224, 224], metavar=('H', 'W'), help='Input image size H W')
    p.add_argument('--output', type=Path, default=DEFAULT_OUTPUT_MODEL, help='Output path for model .h5 file')
    p.add_argument('--seed', type=int, default=123, help='Random seed for split reproducibility')
    return p


def build_model(input_shape: tuple[int, int, int], num_classes: int) -> tf.keras.Model:
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
    ], name='augmentation')

    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.Rescaling(1./255)(inputs)
    x = data_augmentation(x)

    # Simple CNN stack
    for filters in (32, 64, 128):
        x = tf.keras.layers.Conv2D(filters, (3, 3), padding='same', activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.MaxPooling2D()(x)
        x = tf.keras.layers.Dropout(0.25)(x)

    x = tf.keras.layers.Conv2D(256, (3, 3), padding='same', activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    x = tf.keras.layers.Dense(128, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.3)(x)

    if num_classes == 2:
        # Binary classification head
        outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
        loss = 'binary_crossentropy'
        metrics = ['accuracy', tf.keras.metrics.AUC(name='auc')]
    else:
        outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
        loss = 'sparse_categorical_crossentropy'
        metrics = ['accuracy']

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name='mango_cnn')
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss=loss, metrics=metrics)
    return model


def plot_history(history: tf.keras.callbacks.History, out_path: Path) -> None:
    hist = history.history
    plt.figure(figsize=(10, 4))
    # Accuracy
    plt.subplot(1, 2, 1)
    if 'accuracy' in hist:
        plt.plot(hist['accuracy'], label='train_acc')
    if 'val_accuracy' in hist:
        plt.plot(hist['val_accuracy'], label='val_acc')
    plt.title('Accuracy')
    plt.xlabel('Epoch')
    plt.legend()
    # Loss
    plt.subplot(1, 2, 2)
    plt.plot(hist['loss'], label='train_loss')
    if 'val_loss' in hist:
        plt.plot(hist['val_loss'], label='val_loss')
    plt.title('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    args = build_argparser().parse_args()

    data_dir: Path = args.data_dir.resolve()
    if not data_dir.exists():
        raise SystemExit(f"Dataset directory not found: {data_dir}")

    img_height, img_width = args.img_size
    batch_size = args.batch_size

    # Use the modern utility which works with nested class subfolders
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset='training',
        seed=args.seed,
        image_size=(img_height, img_width),
        batch_size=batch_size,
        label_mode='int',
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset='validation',
        seed=args.seed,
        image_size=(img_height, img_width),
        batch_size=batch_size,
        label_mode='int',
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"Classes: {class_names}")

    # Cache and prefetch for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # Build and train model
    model = build_model((img_height, img_width, 3), num_classes)
    model.summary()

    # Callbacks
    ckpt_cb = tf.keras.callbacks.ModelCheckpoint(
        filepath=str(args.output),
        monitor='val_accuracy',
        save_best_only=True,
        save_weights_only=False,
        verbose=1,
    )
    early_cb = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=5, restore_best_weights=True
    )
    reduce_lr_cb = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3, verbose=1
    )

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=[ckpt_cb, early_cb, reduce_lr_cb],
    )

    # Save final model too (best already saved by checkpoint)
    model.save(args.output)

    # Save artifacts
    DEFAULT_LABELS_JSON.write_text(json.dumps({i: name for i, name in enumerate(class_names)}, indent=2))
    DEFAULT_HISTORY_JSON.write_text(json.dumps(history.history, indent=2))
    plot_history(history, DEFAULT_TRAINING_PLOT)

    print(f"\nTraining complete. Artifacts saved to:\n- Model: {args.output}\n- Labels: {DEFAULT_LABELS_JSON}\n- History: {DEFAULT_HISTORY_JSON}\n- Plot: {DEFAULT_TRAINING_PLOT}")


if __name__ == '__main__':
    main()
