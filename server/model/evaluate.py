"""
Evaluate the trained mango model on a directory dataset and export metrics and charts.

Usage (from repo root or server/model):
  python server/model/evaluate.py --data-dir ./dataset --split validation --img-size 224 224 --batch-size 32

Outputs (under server/model/metrics/):
  - metrics.json: overall accuracy, per-class precision/recall/f1/support
  - confusion_matrix.png: confusion matrix heatmap
  - class_distribution_pie.png: dataset class distribution
  - per_class_accuracy_bar.png: per-class accuracy bar chart
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

THIS_DIR = Path(__file__).resolve().parent
METRICS_DIR = THIS_DIR / 'metrics'


def build_argparser():
    p = argparse.ArgumentParser(description='Evaluate the mango classifier and plot metrics.')
    p.add_argument('--data-dir', type=Path, default=(THIS_DIR.parent.parent / 'dataset'))
    p.add_argument('--img-size', type=int, nargs=2, default=[224, 224])
    p.add_argument('--batch-size', type=int, default=32)
    p.add_argument('--split', choices=['validation', 'training', 'full'], default='validation',
                   help='Which split to evaluate. If full, uses all data without split.')
    p.add_argument('--model', type=Path, default=(THIS_DIR / 'mango_model.h5'))
    return p


def load_dataset(data_dir: Path, img_size: tuple[int, int], batch_size: int, split: str, seed: int = 123):
    if split == 'full':
        ds = tf.keras.utils.image_dataset_from_directory(
            data_dir, image_size=img_size, batch_size=batch_size, label_mode='int', shuffle=False
        )
        return ds
    else:
        subset = 'validation' if split == 'validation' else 'training'
        ds = tf.keras.utils.image_dataset_from_directory(
            data_dir, validation_split=0.2, subset=subset, seed=seed,
            image_size=img_size, batch_size=batch_size, label_mode='int', shuffle=False
        )
        return ds


def plot_confusion_matrix(y_true, y_pred, class_names, out_png: Path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def plot_class_distribution(ds, out_png: Path):
    # Collect labels from dataset
    labels = []
    for _, y in ds:
        labels.extend(y.numpy().tolist())
    labels = np.array(labels)
    counts = [(labels == i).sum() for i in range(len(ds.class_names))]
    plt.figure(figsize=(5, 4))
    plt.pie(counts, labels=ds.class_names, autopct='%1.1f%%', startangle=140)
    plt.title('Class Distribution')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def plot_per_class_accuracy(y_true, y_pred, class_names, out_png: Path):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    accs = []
    for i, _ in enumerate(class_names):
        mask = (y_true == i)
        if mask.any():
            accs.append((y_pred[mask] == i).mean())
        else:
            accs.append(0.0)
    plt.figure(figsize=(6, 4))
    plt.bar(class_names, [a * 100 for a in accs], color=['#f59e0b', '#16a34a', '#3b82f6', '#ef4444'][:len(class_names)])
    plt.ylabel('Accuracy (%)')
    plt.title('Per-class Accuracy')
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def main():
    args = build_argparser().parse_args()
    data_dir = args.data_dir.resolve()
    if not data_dir.exists():
        raise SystemExit(f'Dataset not found: {data_dir}')

    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    ds = load_dataset(data_dir, tuple(args.img_size), args.batch_size, args.split)
    class_names = ds.class_names

    model_path = args.model.resolve()
    if not model_path.exists():
        raise SystemExit(f'Model not found: {model_path}. Train first.')
    model = tf.keras.models.load_model(str(model_path), compile=False)

    # Ensure preprocessing consistent with training
    # If model expects [0,1] scaling and includes a Rescaling layer, inference will still work.
    y_true_all = []
    y_pred_all = []
    for x_batch, y_batch in ds:
        # Convert to float32 to avoid dtype issues
        x_batch = tf.cast(x_batch, tf.float32)
        # If values seem 0..255, scale to 0..1 for robustness
        if tf.reduce_max(x_batch) > 1.5:
            x_batch = x_batch / 255.0
        logits = model.predict(x_batch, verbose=0)
        if logits.shape[-1] == 1:
            # Binary head
            probs1 = tf.squeeze(tf.sigmoid(logits), axis=-1).numpy()
            preds = (probs1 >= 0.5).astype(int)
        else:
            preds = tf.argmax(logits, axis=-1).numpy()
        y_true_all.extend(y_batch.numpy().tolist())
        y_pred_all.extend(preds.tolist())

    acc = accuracy_score(y_true_all, y_pred_all)
    # Ensure classification_report includes all classes even if some are absent in y_true
    labels = list(range(len(class_names)))
    report = classification_report(
        y_true_all,
        y_pred_all,
        labels=labels,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    # Save metrics
    metrics = {
        'overall_accuracy': acc,
        'per_class': {cls: {
            'precision': report[cls]['precision'],
            'recall': report[cls]['recall'],
            'f1': report[cls]['f1-score'],
            'support': int(report[cls]['support'])
        } for cls in class_names}
    }
    (METRICS_DIR / 'metrics.json').write_text(json.dumps(metrics, indent=2))

    # Plots
    plot_confusion_matrix(y_true_all, y_pred_all, class_names, METRICS_DIR / 'confusion_matrix.png')
    plot_class_distribution(ds, METRICS_DIR / 'class_distribution_pie.png')
    plot_per_class_accuracy(y_true_all, y_pred_all, class_names, METRICS_DIR / 'per_class_accuracy_bar.png')

    print('\nEvaluation complete. Outputs saved under:', METRICS_DIR)


if __name__ == '__main__':
    main()
