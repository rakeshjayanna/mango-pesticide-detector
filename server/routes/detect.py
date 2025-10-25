from flask import Blueprint, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf
from pathlib import Path
import json
import joblib


# Blueprint for detection routes
detect_bp = Blueprint('detect', __name__)
@detect_bp.route('/health', methods=['GET'])
def health():
    """Lightweight health endpoint to verify API is reachable and model presence."""
    model_path = (_model_dir() / 'mango_model.h5')
    best = _get_best_model_name()
    return jsonify({
        'status': 'ok',
        'model_present': model_path.exists(),
        'best_model': best,
    })



# Globals for lazy-loaded model and metadata
MODEL = None
FEATURE_EXTRACTOR = None
SVM_MODEL = None
RF_MODEL = None
INPUT_SIZE = (224, 224)
CLASS_NAMES = None  # List[str]


def _model_dir() -> Path:
    return Path(__file__).resolve().parent.parent / 'model'


def _load_labels(model_dir: Path) -> list[str] | None:
    labels_file = model_dir / 'class_indices.json'
    if labels_file.exists():
        try:
            mapping = json.loads(labels_file.read_text())
            # mapping is index -> name
            items = sorted(((int(k), v) for k, v in mapping.items()), key=lambda kv: kv[0])
            return [name for _, name in items]
        except Exception:
            pass
    # Fallback order
    return ['organic', 'pesticide']


def _comparison_json_path() -> Path:
    return _model_dir() / 'metrics' / 'model_comparison.json'


def _best_model_json_path() -> Path:
    return _model_dir() / 'best_model.json'


def _get_best_model_name() -> str | None:
    p = _best_model_json_path()
    if p.exists():
        try:
            data = json.loads(p.read_text())
            return data.get('best_model')
        except Exception:
            return None
    return None


def _load_model():
    global MODEL, INPUT_SIZE, CLASS_NAMES
    if MODEL is not None:
        return
    model_dir = _model_dir()
    model_path = model_dir / 'mango_model.h5'
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Train and save the model first.")
    MODEL = tf.keras.models.load_model(str(model_path), compile=False)
    # Infer input size from model input tensor
    try:
        ishape = MODEL.inputs[0].shape
        h = int(ishape[1]) if ishape[1] is not None else 224
        w = int(ishape[2]) if ishape[2] is not None else 224
        INPUT_SIZE = (h, w)
    except Exception:
        INPUT_SIZE = (224, 224)
    CLASS_NAMES = _load_labels(model_dir)


def _load_feature_models():
    """Lazy-load feature extractor and sklearn models if present."""
    global FEATURE_EXTRACTOR, SVM_MODEL, RF_MODEL
    if FEATURE_EXTRACTOR is None and MODEL is not None:
        # Penultimate layer features
        try:
            # Try to pick the last Dense layer output as features
            penultimate = None
            for layer in reversed(MODEL.layers):
                if isinstance(layer, tf.keras.layers.Dense):
                    penultimate = layer
                    break
            output_tensor = penultimate.output if penultimate is not None else MODEL.layers[-2].output
            FEATURE_EXTRACTOR = tf.keras.Model(inputs=MODEL.input, outputs=output_tensor)
        except Exception:
            FEATURE_EXTRACTOR = None
    models_dir = _model_dir() / 'models'
    svm_path = models_dir / 'svm.pkl'
    rf_path = models_dir / 'rf.pkl'
    if SVM_MODEL is None and svm_path.exists():
        try:
            SVM_MODEL = joblib.load(svm_path)
        except Exception:
            SVM_MODEL = None
    if RF_MODEL is None and rf_path.exists():
        try:
            RF_MODEL = joblib.load(rf_path)
        except Exception:
            RF_MODEL = None


def _reset_models():
    """Reset cached models and metadata so they can be reloaded from disk."""
    global MODEL, FEATURE_EXTRACTOR, SVM_MODEL, RF_MODEL, INPUT_SIZE, CLASS_NAMES
    MODEL = None
    FEATURE_EXTRACTOR = None
    SVM_MODEL = None
    RF_MODEL = None
    INPUT_SIZE = (224, 224)
    CLASS_NAMES = None


def _preprocess_image(file_storage) -> np.ndarray:
    # Open with PIL, convert to RGB, resize to model input
    img = Image.open(file_storage.stream).convert('RGB')
    img = img.resize((INPUT_SIZE[1], INPUT_SIZE[0]))  # (width, height)
    x = np.array(img, dtype=np.float32)
    # If model includes Rescaling layer, values can be 0..255; model handles scaling.
    # To be robust, normalize only when values appear unscaled.
    if x.max() > 1.5:
        x = x / 255.0
    x = np.expand_dims(x, axis=0)
    return x


def _preprocess_raw_image(file_storage) -> np.ndarray:
    """Preprocess without manual scaling (for feature extractor that includes rescaling)."""
    img = Image.open(file_storage.stream).convert('RGB')
    img = img.resize((INPUT_SIZE[1], INPUT_SIZE[0]))
    x = np.array(img, dtype=np.float32)  # 0..255
    x = np.expand_dims(x, axis=0)
    return x


def _validate_mango_image(cnn_conf, svm_conf, rf_conf, threshold=0.50):
    """Check if image is likely a mango based on model confidences.
    Returns (is_valid, reason)
    """
    confidences = [c for c in [cnn_conf, svm_conf, rf_conf] if c is not None]
    if not confidences:
        return False, "No valid predictions available"
    
    max_conf = max(confidences)
    avg_conf = sum(confidences) / len(confidences)
    
    # If the highest confidence is below threshold, likely not a mango
    if max_conf < threshold:
        return False, f"Low confidence ({max_conf*100:.1f}%) - image may not be a mango"
    
    # If average confidence is too low, likely not a mango
    if avg_conf < (threshold * 0.8):  # 40% for 50% threshold
        return False, f"Average confidence too low ({avg_conf*100:.1f}%) - image may not be a mango"
    
    return True, "Valid mango image"


def _compare_on_image(file_storage):
    """Shared logic: run CNN, SVM, RF on an image, choose model by validation accuracy or per-image confidence.
    Returns dict: { models: {cnn|svm|random_forest: {label, confidence%}}, selection: {model, reason, detail}, final: {label, confidence%} }
    """
    # Ensure models are loaded
    _load_model()
    _load_feature_models()

    # CNN prediction (scaled input for robustness)
    x_scaled = _preprocess_image(file_storage)
    preds = MODEL.predict(x_scaled, verbose=0)
    if preds.shape[-1] == 1:
        p1 = float(preds[0][0])
        cnn_idx = 1 if p1 >= 0.5 else 0
        cnn_conf = p1 if cnn_idx == 1 else (1.0 - p1)
    else:
        probs = tf.nn.softmax(preds[0]).numpy().tolist()
        cnn_idx = int(np.argmax(probs))
        cnn_conf = float(probs[cnn_idx])
    cnn_label = CLASS_NAMES[cnn_idx] if CLASS_NAMES and cnn_idx < len(CLASS_NAMES) else str(cnn_idx)

    # Feature-based predictions
    xr = _preprocess_raw_image(file_storage)
    feats = FEATURE_EXTRACTOR.predict(xr, verbose=0) if FEATURE_EXTRACTOR is not None else None
    svm_label = svm_conf = rf_label = rf_conf = None
    if feats is not None and SVM_MODEL is not None:
        try:
            if hasattr(SVM_MODEL, 'predict_proba'):
                proba = SVM_MODEL.predict_proba(feats)[0]
                si = int(np.argmax(proba))
                svm_conf = float(proba[si])
            else:
                si = int(SVM_MODEL.predict(feats)[0])
                svm_conf = 1.0
            svm_label = CLASS_NAMES[si] if CLASS_NAMES and si < len(CLASS_NAMES) else str(si)
        except Exception:
            svm_label = svm_conf = None
    if feats is not None and RF_MODEL is not None:
        try:
            if hasattr(RF_MODEL, 'predict_proba'):
                proba = RF_MODEL.predict_proba(feats)[0]
                ri = int(np.argmax(proba))
                rf_conf = float(proba[ri])
            else:
                ri = int(RF_MODEL.predict(feats)[0])
                rf_conf = 1.0
            rf_label = CLASS_NAMES[ri] if CLASS_NAMES and ri < len(CLASS_NAMES) else str(ri)
        except Exception:
            rf_label = rf_conf = None

    # Validate if this is a mango image
    is_valid, validation_msg = _validate_mango_image(cnn_conf, svm_conf, rf_conf)
    if not is_valid:
        return {'error': validation_msg, 'is_mango': False}

    models = {
        'cnn': {'label': cnn_label, 'confidence': round(cnn_conf * 100.0, 2)},
    }
    if svm_label is not None and svm_conf is not None:
        models['svm'] = {'label': svm_label, 'confidence': round(svm_conf * 100.0, 2)}
    if rf_label is not None and rf_conf is not None:
        models['random_forest'] = {'label': rf_label, 'confidence': round(rf_conf * 100.0, 2)}

    # Decide selection: prefer highest validation accuracy
    reason = ''
    best_model = 'cnn'
    accs = {'cnn': None, 'svm': None, 'random_forest': None}
    comp_path = _comparison_json_path()
    if comp_path.exists():
        try:
            comp = json.loads(comp_path.read_text())
            accs['cnn'] = float(comp['models'].get('cnn', {}).get('accuracy', 0.0))
            accs['svm'] = float(comp['models'].get('svm', {}).get('accuracy', 0.0))
            accs['random_forest'] = float(comp['models'].get('random_forest', {}).get('accuracy', 0.0))
            available = {k: v for k, v in accs.items() if k in models and v is not None}
            if available:
                best_model = max(available.keys(), key=lambda k: available[k])
                reason = 'highest validation accuracy'
        except Exception:
            pass
    if not reason:
        best_model = max(models.keys(), key=lambda k: models[k]['confidence'])
        reason = 'highest confidence on this image'

    final = models.get(best_model)
    selection = {
        'model': best_model,
        'reason': reason,
        'detail': {
            'cnn_acc': accs['cnn'] if accs['cnn'] is not None else 0.0,
            'svm_acc': accs['svm'] if accs['svm'] is not None else 0.0,
            'rf_acc': accs['random_forest'] if accs['random_forest'] is not None else 0.0,
        }
    }

    return {'models': models, 'selection': selection, 'final': final}


@detect_bp.route('/detect', methods=['POST'])
def detect():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'no image provided'}), 400
        res = _compare_on_image(request.files['image'])
        
        # Check if image was rejected as non-mango
        if 'error' in res and 'is_mango' in res:
            return jsonify(res), 400
        
        # Keep backward compatibility: return label/confidence, plus model_used
        final = res.get('final') or {}
        payload = {
            'label': final.get('label'),
            'confidence': final.get('confidence'),
            'model_used': res.get('selection', {}).get('model')
        }
        # Also include full comparison so the frontend can show charts without re-upload
        payload['models'] = res.get('models')
        payload['selection'] = res.get('selection')
        return jsonify(payload)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'prediction failed: {str(e)}'}), 500


@detect_bp.route('/models/comparison', methods=['GET'])
def models_comparison():
    p = _comparison_json_path()
    if not p.exists():
        return jsonify({'error': 'comparison metrics not found. Run compare_models.py first.'}), 404
    try:
        data = json.loads(p.read_text())
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'failed to read comparison metrics: {str(e)}'}), 500


@detect_bp.route('/reload', methods=['POST'])
def reload_models():
    """Reload CNN and sklearn models from disk without restarting the server."""
    try:
        _reset_models()
        _load_model()  # load CNN
        _load_feature_models()  # load feature extractor + sklearn models
        models_dir = _model_dir() / 'models'
        return jsonify({
            'status': 'reloaded',
            'model_present': True,
            'svm_present': (models_dir / 'svm.pkl').exists(),
            'rf_present': (models_dir / 'rf.pkl').exists(),
        })
    except FileNotFoundError as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@detect_bp.route('/compare-image', methods=['POST'])
def compare_image():
    """Run CNN, SVM, and RandomForest on the same uploaded image and choose according to validation accuracy.
    If validation metrics are missing, fall back to highest confidence on this image.
    Returns per-model label+confidence, chosen model, reason, and final prediction.
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'no image provided'}), 400
        res = _compare_on_image(request.files['image'])
        
        # Check if image was rejected as non-mango
        if 'error' in res and 'is_mango' in res:
            return jsonify(res), 400
            
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': f'compare failed: {str(e)}'}), 500
