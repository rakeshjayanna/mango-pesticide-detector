# 🥭 Mango Pesticide Detector

A full-stack machine learning application that detects whether a mango is organic or pesticide-treated using three different ML models: CNN (Convolutional Neural Network), SVM (Support Vector Machine), and Random Forest. The system automatically selects the best model based on validation accuracy and displays confidence comparisons.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange)
![Flask](https://img.shields.io/badge/Flask-3.0-green)

## ✨ Features

- 🤖 **Multi-Model Detection**: Combines CNN, SVM, and Random Forest models
- 📊 **Smart Model Selection**: Automatically uses the best-performing model
- 📈 **Confidence Comparison**: Visual charts showing all model predictions
- 🖼️ **Image Validation**: Rejects non-mango images with confidence thresholds
- 🎨 **Modern UI**: Beautiful React interface with animations
- 📱 **Responsive Design**: Works on desktop and mobile
- 🔄 **Hot Reload**: Backend models can be reloaded without restart

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ (Tailwind CSS, Framer Motion, Chart.js)
│   Port: 3000    │
└────────┬────────┘
         │ HTTP REST API
         ▼
┌─────────────────┐
│  Flask Backend  │ (Python, Flask-CORS)
│   Port: 5000    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    ▼         ▼          ▼           ▼
  CNN      SVM      Random       Feature
 Model    Model     Forest      Extractor
(.h5)    (.pkl)    (.pkl)
```

## 🚀 Quick Start (Development)

### Prerequisites

- Python 3.9+ (3.11 recommended)
- Node.js 16+ and npm
- At least 4GB RAM (for TensorFlow)

### 1. Clone and Setup

```powershell
cd "c:\Users\rakes\Desktop\perfect project\mango-pesticide-detector"
```

### 2. Backend Setup

```powershell
cd server

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Server runs on `http://localhost:5000`

### 3. Frontend Setup

```powershell
cd client

# Install dependencies
npm install

# Start development server
npm start
```

Frontend opens automatically at `http://localhost:3000`

### 4. Train Models (Required for first run)

Prepare your dataset:
```
dataset/
  organic/
    img1.jpg
    img2.jpg
    ...
  pesticide/
    img1.jpg
    img2.jpg
    ...
```

Train the CNN model:
```powershell
python .\server\model\model_trainer.py --data-dir .\dataset --epochs 15 --img-size 224 224 --batch-size 32
```

Train comparison models (SVM & Random Forest):
```powershell
python .\server\model\compare_models.py --data-dir .\dataset --img-size 224 224
```

Outputs saved to `server/model/`:
- `mango_model.h5` — CNN model
- `models/svm.pkl` — SVM model
- `models/rf.pkl` — Random Forest model
- `model_comparison.json` — validation accuracies
- `metrics/` — evaluation charts and metrics

### 5. Evaluate Models

```powershell
python .\server\model\evaluate.py --data-dir .\dataset --split validation --img-size 224 224
```

Generates:
- `metrics.json` — accuracy, precision, recall, F1-score
- `confusion_matrix.png` — confusion matrix heatmap
- `class_distribution_pie.png` — dataset distribution
- `per_class_accuracy_bar.png` — per-class accuracy

## 📖 Usage

1. **Upload Image**: Drag & drop or click to upload a mango image
2. **Detection**: System runs all 3 models and selects the best prediction
3. **View Results**: See if it's organic or pesticide-treated with confidence score
4. **Compare Models**: Click "View comparison chart" to see all model predictions
5. **Inline Chart**: Mini-chart shows model comparisons right on the home page

### Image Validation

The system rejects non-mango images by checking:
- Maximum confidence must be ≥ 50%
- Average confidence across models ≥ 40%

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Check backend status and model availability |
| `/api/detect` | POST | Upload image and get prediction with full comparison |
| `/api/compare-image` | POST | Get detailed model comparison for uploaded image |
| `/api/models/comparison` | GET | Get pre-computed validation accuracies |
| `/api/reload` | POST | Hot-reload models without restarting server |

## 📁 Project Structure

```
mango-pesticide-detector/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/       # React components (Upload, Navbar, etc.)
│   │   ├── pages/           # Pages (Home, Compare)
│   │   ├── hooks/           # Custom hooks (useBackendHealth)
│   │   └── config/          # API configuration
│   ├── public/              # Static assets
│   ├── Dockerfile           # Docker config for frontend
│   └── package.json         # Node dependencies
│
├── server/                   # Flask backend
│   ├── routes/
│   │   └── detect.py        # API endpoints
│   ├── model/
│   │   ├── model_trainer.py      # Train CNN
│   │   ├── compare_models.py     # Train SVM & RF
│   │   ├── evaluate.py           # Model evaluation
│   │   ├── mango_model.h5        # Trained CNN
│   │   ├── models/               # SVM & RF models
│   │   └── metrics/              # Evaluation results
│   ├── app.py               # Flask application
│   ├── wsgi.py              # WSGI entry point
│   ├── Dockerfile           # Docker config for backend
│   └── requirements.txt     # Python dependencies
│
├── dataset/                 # Training dataset (not included)
├── docker-compose.yml       # Docker Compose config
├── render.yaml             # Render deployment config
├── railway.json            # Railway deployment config
├── DEPLOYMENT.md           # Comprehensive deployment guide
├── QUICKSTART_DEPLOY.md    # Quick deployment instructions
└── README.md              # This file
```

## 🌐 Deployment

See detailed deployment guides:
- **[QUICKSTART_DEPLOY.md](QUICKSTART_DEPLOY.md)** - Fast deployment with Render + Netlify (FREE)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive guide for all platforms

### Quick Deploy Options

| Platform | Backend | Frontend | Cost | Difficulty |
|----------|---------|----------|------|-----------|
| Render + Netlify | ✅ | ✅ | Free | ⭐ Easy |
| Railway | ✅ | ✅ | Free tier | ⭐ Easy |
| Heroku | ✅ | ✅ | Free tier* | ⭐⭐ Medium |
| Docker | ✅ | ✅ | Self-hosted | ⭐⭐ Medium |
| AWS/Azure/GCP | ✅ | ✅ | Pay-as-you-go | ⭐⭐⭐ Hard |

**Recommended for students:** Render (backend) + Netlify (frontend) = 100% FREE

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at `http://localhost:3000`

## 🧪 Testing

### Backend Health Check
```powershell
curl http://localhost:5000/api/health
```

### Test Detection
```powershell
curl -X POST http://localhost:5000/api/detect -F "image=@path/to/mango.jpg"
```

## 📊 Model Performance

The system compares three models:

| Model | Type | Strengths |
|-------|------|-----------|
| **CNN** | Deep Learning | Best for complex image patterns, spatial features |
| **SVM** | Classical ML | Good generalization, works well with limited data |
| **Random Forest** | Ensemble | Robust, handles noise well |

The best model is selected based on validation accuracy computed during training.

## 🔧 Configuration

### Backend Environment Variables

```env
FLASK_ENV=production
CORS_ORIGINS=https://your-frontend.com
PYTHON_VERSION=3.11.0
```

### Frontend Environment Variables

```env
REACT_APP_API_URL=https://your-backend.com/api
```

## 📝 Development Notes

### Hot Reload Models
After retraining models, reload without restarting:
```powershell
curl -X POST http://localhost:5000/api/reload
```

### Update Model Comparison
After retraining CNN:
```powershell
python .\server\model\compare_models.py --data-dir .\dataset
```

### Adjust Image Validation Threshold
Edit `server/routes/detect.py`, function `_validate_mango_image()`:
```python
def _validate_mango_image(cnn_conf, svm_conf, rf_conf, threshold=0.50):
    # Change threshold value (default: 0.50 = 50%)
```

## 🎓 Academic Use

Perfect for:
- Machine Learning course projects
- Computer Vision assignments
- Agriculture technology research
- Comparative ML model studies

### Presentation Tips
1. Demo with 2-3 mango images (organic + pesticide)
2. Show rejection of non-mango image
3. Explain model comparison chart
4. Discuss accuracy metrics from evaluation
5. Show the multi-model architecture diagram

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check model files exist
ls server\model\mango_model.h5
ls server\model\models\svm.pkl
```

### Frontend can't connect
- Verify backend is running: `curl http://localhost:5000/api/health`
- Check CORS settings in `server/app.py`
- Clear browser cache and reload
- Check browser console for errors

### Models not loading
- Ensure model files exist in `server/model/`
- Check file permissions
- View Flask logs for detailed error messages
- Try retraining models

### Low accuracy
- Add more training data (recommended: 500+ images per class)
- Increase epochs: `--epochs 30`
- Try data augmentation
- Balance dataset (equal organic/pesticide samples)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- TensorFlow and Keras teams for the deep learning framework
- Scikit-learn for classical ML algorithms
- React team for the amazing frontend library
- Flask for the lightweight backend framework

## 📧 Support

For issues and questions:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Check [QUICKSTART_DEPLOY.md](QUICKSTART_DEPLOY.md) for quick start
- Open an issue on GitHub
- Check existing issues for solutions

---

**Made with ❤️ for agriculture technology and machine learning education**
