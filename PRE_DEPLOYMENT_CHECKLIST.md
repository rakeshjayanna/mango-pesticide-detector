# 🚀 Pre-Deployment Checklist

Use this checklist before deploying your application.

## ✅ Code Preparation

### Backend
- [ ] All model files exist in `server/model/`:
  - [ ] `mango_model.h5` (CNN model)
  - [ ] `models/svm.pkl` (SVM model)
  - [ ] `models/rf.pkl` (Random Forest model)
  - [ ] `model_comparison.json` (validation metrics)
  - [ ] `metrics/metrics.json` (evaluation results)

- [ ] `requirements.txt` is up to date
- [ ] CORS configuration updated in `server/app.py` for production
- [ ] All imports working (test with `python -c "import tensorflow"`)
- [ ] No hardcoded localhost URLs in code

### Frontend
- [ ] All dependencies installed (`npm install` runs without errors)
- [ ] Build succeeds (`npm run build` completes)
- [ ] No console errors in development mode
- [ ] API configuration ready in `src/config/api.js`
- [ ] Environment variables documented in `.env.example`

### General
- [ ] `.gitignore` properly configured
- [ ] README.md is complete and accurate
- [ ] Sensitive data removed (API keys, passwords, etc.)
- [ ] Git repository initialized
- [ ] All changes committed

## 📦 Model Files

Choose your strategy for large model files:

### Option 1: Git LFS (Recommended if files < 500MB)
```bash
git lfs install
git lfs track "*.h5"
git lfs track "*.pkl"
git add .gitattributes
git add server/model/
git commit -m "Add model files with LFS"
```

### Option 2: Manual Upload After Deployment
- [ ] Models documented for manual upload
- [ ] Upload script or instructions prepared
- [ ] Tested manual upload process

### Option 3: Cloud Storage (Best for large files)
- [ ] Models uploaded to S3/GCS/Azure Blob
- [ ] Download script added to backend startup
- [ ] Credentials configured securely

## 🌐 Deployment Platform Setup

### For Render + Netlify (Recommended)

#### Backend (Render)
- [ ] GitHub repository is public (or Render connected)
- [ ] `render.yaml` configured
- [ ] Environment variables documented:
  - [ ] `FLASK_ENV=production`
  - [ ] `CORS_ORIGINS=<frontend-url>`
- [ ] Health check endpoint working (`/api/health`)
- [ ] Build command verified: `pip install -r requirements.txt`
- [ ] Start command verified: `gunicorn wsgi:app`

#### Frontend (Netlify)
- [ ] Production build tested locally
- [ ] `build/` folder generated successfully
- [ ] Environment variables documented:
  - [ ] `REACT_APP_API_URL=<backend-url>/api`
- [ ] Redirects configured for React Router (in `public/_redirects`)

### For Railway
- [ ] `railway.json` configured
- [ ] Repository connected
- [ ] Environment variables ready

### For Heroku
- [ ] `Procfile` exists for both frontend and backend
- [ ] `runtime.txt` specifies Python version (if needed)
- [ ] Heroku CLI installed
- [ ] Heroku apps created

### For Docker
- [ ] Docker installed and running
- [ ] `Dockerfile` tested for backend
- [ ] `Dockerfile` tested for frontend
- [ ] `docker-compose.yml` tested locally
- [ ] Images build without errors
- [ ] Containers start successfully

## 🧪 Testing Before Deployment

### Local Testing
- [ ] Backend health check: `curl http://localhost:5000/api/health`
- [ ] Frontend loads: `http://localhost:3000`
- [ ] Upload organic mango image → correct prediction
- [ ] Upload pesticide mango image → correct prediction
- [ ] Upload non-mango image → properly rejected
- [ ] View comparison chart → all 3 models shown
- [ ] Inline chart displays correctly
- [ ] No console errors
- [ ] No network errors (check browser DevTools)

### Production Build Testing
```powershell
# Backend
cd server
waitress-serve --host=127.0.0.1 --port=5000 wsgi:app

# Frontend
cd client
npm run build
serve -s build -l 3000
```

- [ ] Production frontend connects to backend
- [ ] All features work in production mode
- [ ] No CORS errors
- [ ] Images upload successfully
- [ ] Charts render correctly

## 📝 Documentation

- [ ] README.md complete with:
  - [ ] Project description
  - [ ] Setup instructions
  - [ ] Usage guide
  - [ ] API documentation
  - [ ] Deployment links (once deployed)
  
- [ ] DEPLOYMENT.md reviewed
- [ ] QUICKSTART_DEPLOY.md reviewed
- [ ] Environment variables documented
- [ ] Known issues documented

## 🔒 Security

- [ ] No API keys in code
- [ ] No database passwords in code
- [ ] `.env` files in `.gitignore`
- [ ] CORS properly restricted for production
- [ ] File upload size limits configured (5MB)
- [ ] File type validation in place
- [ ] No sensitive data in git history

## 🎨 UI/UX

- [ ] All images and assets loaded
- [ ] Responsive design works on mobile
- [ ] Loading states implemented
- [ ] Error messages user-friendly
- [ ] Success feedback clear
- [ ] Navigation works smoothly
- [ ] Drag-and-drop tested

## 📊 Performance

- [ ] Model loading optimized (lazy loading implemented)
- [ ] Image preprocessing efficient
- [ ] Frontend bundle size reasonable
- [ ] API response times acceptable
- [ ] No memory leaks detected

## 🎓 Academic Presentation Ready

- [ ] 2-3 sample images prepared:
  - [ ] Organic mango image
  - [ ] Pesticide mango image
  - [ ] Non-mango image (for rejection demo)
  
- [ ] Demo flow practiced:
  1. [ ] Show homepage
  2. [ ] Upload organic mango
  3. [ ] Show prediction result
  4. [ ] Show inline comparison chart
  5. [ ] Click "View comparison chart"
  6. [ ] Explain 3-model comparison
  7. [ ] Upload non-mango image
  8. [ ] Show rejection message
  
- [ ] Architecture diagram ready
- [ ] Metrics and evaluation results ready
- [ ] Confusion matrix image accessible
- [ ] Can explain:
  - [ ] Why use 3 models?
  - [ ] How is best model selected?
  - [ ] What is image validation threshold?
  - [ ] What features does CNN extract?

## 🚀 Final Steps

### Before Pushing to GitHub
```bash
# Review all files to be committed
git status

# Check for sensitive data
git diff

# Ensure .gitignore is working
git check-ignore -v <file>
```

### After Deployment
- [ ] Backend URL accessible and returns 200 OK
- [ ] Frontend URL loads application
- [ ] Test full user flow on deployed version
- [ ] Check browser console for errors
- [ ] Test from different devices/browsers
- [ ] Monitor application logs for issues
- [ ] Update README with live demo URLs

### Share Your Work
- [ ] Add deployment URLs to README
- [ ] Create demo video/screenshots
- [ ] Prepare project presentation
- [ ] Document lessons learned
- [ ] Share with your team/instructor

## 📞 Emergency Contacts

**If deployment fails:**
1. Check platform status page
2. Review deployment logs
3. Verify all files are committed
4. Check environment variables
5. Test locally first
6. Consult platform documentation
7. Check GitHub issues for similar problems

**Helpful Resources:**
- Render Docs: https://render.com/docs
- Netlify Docs: https://docs.netlify.com
- Railway Docs: https://docs.railway.app
- Docker Docs: https://docs.docker.com

---

## ✨ You're Ready!

Once all boxes are checked, you're ready to deploy! 🎉

Choose your deployment method from `QUICKSTART_DEPLOY.md` and follow the steps.

**Good luck with your deployment!** 🚀
