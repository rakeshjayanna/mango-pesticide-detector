# Deployment Quick Start Guide

## 🚀 Easiest Deployment (Free) - Render + Netlify

### Step 1: Prepare Your Code

1. **Push to GitHub:**
```bash
cd "c:\Users\rakes\Desktop\perfect project\mango-pesticide-detector"
git init
git add .
git commit -m "Initial commit - Mango Pesticide Detector"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy Backend (Render)

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `mango-backend`
   - **Root Directory:** `server`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Plan:** Free
5. Click "Create Web Service"
6. **Important:** Upload your model files (`mango_model.h5`, `svm.pkl`, `rf.pkl`) to the server:
   - Use Render's SSH or file upload feature
   - Or include them in your git repo with Git LFS

7. **Copy your backend URL** (e.g., `https://mango-backend.onrender.com`)

### Step 3: Deploy Frontend (Netlify)

1. **Build the frontend locally:**
```powershell
cd client
npm install
npm run build
```

2. Go to [netlify.com](https://netlify.com) and sign up
3. Drag and drop the `client/build` folder onto Netlify
4. After deployment, go to "Site settings" → "Environment variables"
5. Add: 
   - **Key:** `REACT_APP_API_URL`
   - **Value:** `https://mango-backend.onrender.com/api` (your Render URL)
6. Trigger a redeploy

### Step 4: Update CORS

Update `server/app.py` line 9:
```python
allowed_origins = os.getenv('CORS_ORIGINS', 'https://your-netlify-site.netlify.app')
```

Or add environment variable in Render:
- **Key:** `CORS_ORIGINS`
- **Value:** `https://your-netlify-site.netlify.app`

### Step 5: Test

Visit your Netlify URL and test the application!

---

## 🐳 Docker Deployment (Local or Cloud)

### Build and Run with Docker Compose

```powershell
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

---

## 📦 Local Production Build

### Backend (Windows)

```powershell
cd server
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
```

### Frontend

```powershell
cd client
npm run build
npm install -g serve
serve -s build -l 3000
```

---

## ⚠️ Important Notes

### Model Files
Your model files are large (`.h5`, `.pkl`). Options:

1. **Include in Git** (if < 100MB total):
```bash
git add server/model/*.h5 server/model/*.pkl
```

2. **Use Git LFS** (recommended):
```bash
git lfs install
git lfs track "*.h5"
git lfs track "*.pkl"
git add .gitattributes
git add server/model/
git commit -m "Add model files with LFS"
```

3. **Upload manually** after deployment to Render/Railway

4. **Use cloud storage** (S3, Google Cloud Storage):
   - Store models in cloud
   - Download on app startup

### Environment Variables

**Backend (.env):**
```
FLASK_ENV=production
CORS_ORIGINS=https://your-frontend-url.com
```

**Frontend (.env.production):**
```
REACT_APP_API_URL=https://your-backend-url.com/api
```

---

## 🎓 For Academic Presentation

### Demo Checklist

✅ **Before presenting:**
1. Test both mango images (organic/pesticide) ✓
2. Test non-mango image (should reject) ✓
3. Test comparison chart visualization ✓
4. Prepare 2-3 sample images ✓
5. Check both models are loaded ✓

✅ **During presentation:**
1. Show homepage and UI
2. Upload organic mango → show result
3. Upload pesticide mango → show result
4. Click "View comparison chart" → explain 3 models
5. Upload non-mango image → show rejection
6. Explain the architecture (CNN, SVM, RF)

---

## 🆘 Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Install dependencies
pip install -r requirements.txt

# Check model files exist
ls server/model/
```

**Frontend can't connect:**
- Check if backend is running: `curl http://localhost:5000/api/health`
- Verify CORS settings in `server/app.py`
- Check browser console for errors

**Models not loading:**
- Ensure files exist: `mango_model.h5`, `svm.pkl`, `rf.pkl`
- Check paths in `server/routes/detect.py`
- View backend logs for errors

---

## 📞 Platform Support

- **Render:** https://render.com/docs
- **Netlify:** https://docs.netlify.com
- **Railway:** https://docs.railway.app
- **Heroku:** https://devcenter.heroku.com

---

**Your app is ready to deploy! Choose your platform and follow the steps above.** 🚀
