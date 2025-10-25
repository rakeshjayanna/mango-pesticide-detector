# 🎯 Quick Reference - Deployment Commands

## 📦 Local Development

### Start Backend
```powershell
cd server
.\.venv\Scripts\Activate.ps1
python app.py
```
**URL:** http://localhost:5000

### Start Frontend
```powershell
cd client
npm start
```
**URL:** http://localhost:3000

---

## 🤖 Train/Update Models

### Train CNN Model
```powershell
python .\server\model\model_trainer.py --data-dir .\dataset --epochs 15 --img-size 224 224 --batch-size 32
```

### Train SVM & Random Forest
```powershell
python .\server\model\compare_models.py --data-dir .\dataset --img-size 224 224
```

### Evaluate Models
```powershell
python .\server\model\evaluate.py --data-dir .\dataset --split validation --img-size 224 224
```

### Hot Reload Models (without restart)
```powershell
curl -X POST http://localhost:5000/api/reload
```

---

## 🚀 Deployment Preparation

### Run Preparation Script
```powershell
.\prepare-deploy.ps1
```

### Build Frontend for Production
```powershell
cd client
npm run build
```

### Test Production Backend (Windows)
```powershell
cd server
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
```

### Serve Production Frontend
```powershell
cd client
npm install -g serve
serve -s build -l 3000
```

---

## 🌐 Quick Deploy to Render + Netlify (FREE)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy Backend on Render
1. Go to https://render.com
2. New + → Web Service
3. Connect GitHub repo
4. Configure:
   - **Root Directory:** `server`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
5. Deploy
6. Copy backend URL

### 3. Deploy Frontend on Netlify
1. Build: `cd client && npm run build`
2. Go to https://netlify.com
3. Drag & drop `client/build` folder
4. Add environment variable:
   - `REACT_APP_API_URL` = `https://your-render-url.com/api`
5. Redeploy

---

## 🐳 Docker Commands

### Build and Run
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop
```bash
docker-compose down
```

### Rebuild After Changes
```bash
docker-compose up -d --build
```

---

## 🧪 Testing Commands

### Backend Health Check
```powershell
curl http://localhost:5000/api/health
```

### Test Detection API
```powershell
curl -X POST http://localhost:5000/api/detect -F "image=@path\to\mango.jpg"
```

### Check Backend Logs (Flask)
Just look at terminal where `python app.py` is running

### Check Frontend Build Size
```powershell
cd client\build
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum
```

---

## 📝 Common Git Commands

### Initialize Repository
```bash
git init
git add .
git commit -m "Initial commit"
```

### Check Status
```bash
git status
```

### Create New Branch
```bash
git checkout -b feature-name
```

### Push Changes
```bash
git add .
git commit -m "Description of changes"
git push
```

### Ignore Large Files
Add to `.gitignore`:
```
*.h5
*.pkl
dataset/
```

### Use Git LFS for Large Files
```bash
git lfs install
git lfs track "*.h5"
git lfs track "*.pkl"
git add .gitattributes
git commit -m "Track large files with LFS"
```

---

## 🔧 Environment Variables

### Backend (.env)
```env
FLASK_ENV=production
CORS_ORIGINS=https://your-frontend-url.com
```

### Frontend (.env.production)
```env
REACT_APP_API_URL=https://your-backend-url.com/api
```

---

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check if port 5000 is in use
netstat -ano | findstr :5000
```

### Frontend won't build
```powershell
# Clear cache and reinstall
cd client
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
npm run build
```

### Models not loading
```powershell
# Check model files exist
ls server\model\mango_model.h5
ls server\model\models\svm.pkl
ls server\model\models\rf.pkl

# Check file sizes
Get-Item server\model\*.h5 | Select-Object Name, Length
```

### CORS errors in browser
Update `server/app.py`:
```python
allowed_origins = os.getenv('CORS_ORIGINS', 'https://your-frontend.com')
```

---

## 📊 Check Project Status

### Model Files
```powershell
Get-ChildItem server\model -Recurse -Include *.h5,*.pkl | Select-Object Name, Length
```

### Python Packages
```powershell
cd server
.\.venv\Scripts\Activate.ps1
pip list
```

### Node Packages
```powershell
cd client
npm list --depth=0
```

### Project Size
```powershell
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum
```

---

## 🎓 Demo Preparation

### Start Both Servers
```powershell
# Terminal 1 - Backend
cd server
.\.venv\Scripts\Activate.ps1
python app.py

# Terminal 2 - Frontend
cd client
npm start
```

### Test Images Checklist
- [ ] Organic mango image
- [ ] Pesticide mango image
- [ ] Non-mango image (cat, car, etc.)

### Demo Flow
1. Open http://localhost:3000
2. Upload organic mango → show result
3. Show inline comparison chart
4. Click "View comparison chart"
5. Upload pesticide mango → show result
6. Upload non-mango → show rejection

---

## 📞 Quick Links

- **Render:** https://render.com
- **Netlify:** https://netlify.com
- **Railway:** https://railway.app
- **Docker Hub:** https://hub.docker.com

---

## 💡 Pro Tips

1. **Always test locally before deploying**
2. **Keep model files < 500MB for GitHub**
3. **Use environment variables for URLs**
4. **Test with different images**
5. **Check browser console for errors**
6. **Monitor backend logs during testing**
7. **Use Git LFS for large model files**
8. **Document your environment setup**

---

**Save this file for quick reference!** 📌
