"""
Train and compare CNN vs SVM vs RandomForest on the same dataset split.

This script assumes a trained CNN exists at server/model/mango_model.h5 and uses its
penultimate layer as a feature extractor for classical models (SVM, RandomForest).

Outputs:
- server/model/models/svm.pkl, rf.pkl (scikit-learn models)
- server/model/metrics/model_comparison.json (accuracies and reports)
- server/model/best_model.json (name of best-performing model)

Usage:
  python server/model/compare_models.py --data-dir ./dataset --img-size 224 224 --batch-size 32
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib


THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parent.parent
DEFAULT_DATASET_DIR = (ROOT / 'dataset').resolve()
MODEL_DIR = THIS_DIR
CNN_MODEL_PATH = MODEL_DIR / 'mango_model.h5'
METRICS_DIR = MODEL_DIR / 'metrics'
MODELS_DIR = MODEL_DIR / 'models'
COMPARISON_JSON = METRICS_DIR / 'model_comparison.json'
BEST_JSON = MODEL_DIR / 'best_model.json'
LABELS_JSON = MODEL_DIR / 'class_indices.json'


def build_argparser():
    p = argparse.ArgumentParser(description='Compare CNN vs SVM vs RandomForest classifiers')
    p.add_argument('--data-dir', type=Path, default=DEFAULT_DATASET_DIR, help='Dataset root with class subfolders')
    p.add_argument('--img-size', type=int, nargs=2, default=[224, 224], metavar=('H', 'W'))
    p.add_argument('--batch-size', type=int, default=32)
    p.add_argument('--seed', type=int, default=123)
    return p


def load_dataset(data_dir: Path, img_size: Tuple[int, int], batch_size: int, seed: int):
    h, w = img_size
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset='training',
        seed=seed,
        image_size=(h, w),
        batch_size=batch_size,
        label_mode='int',
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset='validation',
        seed=seed,
        image_size=(h, w),
        batch_size=batch_size,
        label_mode='int',
    )
    class_names = train_ds.class_names
    # Unbatch to arrays
    X_train, y_train = [], []
    for xb, yb in train_ds:
        X_train.append(xb.numpy())
        y_train.append(yb.numpy())
    X_val, y_val = [], []
    for xb, yb in val_ds:
        X_val.append(xb.numpy())
        y_val.append(yb.numpy())
    X_train = np.concatenate(X_train, axis=0)
    y_train = np.concatenate(y_train, axis=0)
    X_val = np.concatenate(X_val, axis=0)
    y_val = np.concatenate(y_val, axis=0)
    return (X_train, y_train), (X_val, y_val), class_names


def build_feature_extractor(cnn_model: tf.keras.Model) -> tf.keras.Model:
    # Use the penultimate layer (before final Dense) as features
    # Typically model.layers[-1] is Dense(num_classes) and model.layers[-2] is Dropout or Dense(128)
    # We want the last Dense(128) output; find the last Dense with units != num_classes
    # Fallback: use layers[-2]
    penultimate = None
    for layer in reversed(cnn_model.layers):
        if isinstance(layer, tf.keras.layers.Dense):
            # Heuristic: pick first Dense encountered from end that is not the final classification layer
            penultimate = layer
            break
    if penultimate is None:
        output_tensor = cnn_model.layers[-2].output
    else:
        output_tensor = penultimate.output
    return tf.keras.Model(inputs=cnn_model.input, outputs=output_tensor)


def extract_features(model: tf.keras.Model, X: np.ndarray, batch_size: int = 64) -> np.ndarray:
    # The CNN includes rescaling/augmentation internally; ensure X is float32 in 0..255 space
    Xf = X.astype('float32')
    feats = model.predict(Xf, batch_size=batch_size, verbose=0)
    return feats


def evaluate_cnn(cnn_model: tf.keras.Model, X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
    logits = cnn_model.predict(X_val, verbose=0)
    if logits.shape[-1] == 1:
        probs = tf.sigmoid(logits).numpy().reshape(-1)
        y_pred = (probs >= 0.5).astype(int)
    else:
        probs = tf.nn.softmax(logits, axis=-1).numpy()
        y_pred = np.argmax(probs, axis=-1)
    acc = float(accuracy_score(y_val, y_pred))
    labels = sorted(list(set(y_val.tolist()) | set(y_pred.tolist())))
    report = classification_report(y_val, y_pred, output_dict=True, labels=labels, zero_division=0)
    cm = confusion_matrix(y_val, y_pred, labels=labels).tolist()
    return {"accuracy": acc, "report": report, "confusion_matrix": cm}


def evaluate_sklearn_model(model, X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
    y_pred = model.predict(X_val)
    acc = float(accuracy_score(y_val, y_pred))
    labels = sorted(list(set(y_val.tolist()) | set(y_pred.tolist())))
    report = classification_report(y_val, y_pred, output_dict=True, labels=labels, zero_division=0)
    cm = confusion_matrix(y_val, y_pred, labels=labels).tolist()
    return {"accuracy": acc, "report": report, "confusion_matrix": cm}


def main():
    args = build_argparser().parse_args()
    data_dir = args.data_dir.resolve()
    img_size = tuple(args.img_size)
    batch = args.batch_size
    seed = args.seed

    if not CNN_MODEL_PATH.exists():
        raise SystemExit(f"CNN model not found: {CNN_MODEL_PATH}. Train it first.")

    (X_train, y_train), (X_val, y_val), class_names = load_dataset(data_dir, img_size, batch, seed)
    # Load CNN and build feature extractor
    cnn = tf.keras.models.load_model(str(CNN_MODEL_PATH), compile=False)
    feat_extractor = build_feature_extractor(cnn)

    # Extract features
    Z_train = extract_features(feat_extractor, X_train)
    Z_val = extract_features(feat_extractor, X_val)

    # Build classical models
    svm = Pipeline([
        ('scaler', StandardScaler()),
        ('svc', SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=seed)),
    ])
    rf = RandomForestClassifier(n_estimators=300, random_state=seed)

    # Fit
    svm.fit(Z_train, y_train)
    rf.fit(Z_train, y_train)

    # Evaluate
    res_cnn = evaluate_cnn(cnn, X_val, y_val)
    res_svm = evaluate_sklearn_model(svm, Z_val, y_val)
    res_rf = evaluate_sklearn_model(rf, Z_val, y_val)

    models_summary = {
        'cnn': res_cnn,
        'svm': res_svm,
        'random_forest': res_rf,
        'class_names': class_names,
    }

    # Determine best by accuracy
    best_name = max(('cnn', 'svm', 'random_forest'), key=lambda k: models_summary[k]['accuracy'])
    best_acc = models_summary[best_name]['accuracy']

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Save sklearn models
    joblib.dump(svm, MODELS_DIR / 'svm.pkl')
    joblib.dump(rf, MODELS_DIR / 'rf.pkl')

    # Save comparison
    comparison_payload = {
        'models': models_summary,
        'best': {'name': best_name, 'accuracy': best_acc},
    }
    COMPARISON_JSON.write_text(json.dumps(comparison_payload, indent=2))

    # Save best model selection
    BEST_JSON.write_text(json.dumps({'best_model': best_name}, indent=2))

    print(f"Comparison complete. Best: {best_name} (acc={best_acc:.4f})")
    print(f"Saved: {COMPARISON_JSON}")


if __name__ == '__main__':
    main()
