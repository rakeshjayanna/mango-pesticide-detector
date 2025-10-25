# Deployment Guide - Mango Pesticide Detector

This guide covers multiple deployment options for your full-stack application.

## Table of Contents
1. [Local Production Build](#local-production-build)
2. [Deploy to Render (Recommended - Free)](#deploy-to-render)
3. [Deploy to Railway](#deploy-to-railway)
4. [Deploy to Heroku](#deploy-to-heroku)
5. [Deploy to AWS/Azure/GCP](#deploy-to-cloud-providers)

---

## Local Production Build

### Backend (Flask + Gunicorn)

1. Install production dependencies:
```bash
cd server
pip install -r requirements.txt
```

2. Run with Gunicorn (Linux/Mac):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

For Windows, use waitress instead:
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
```

### Frontend (React Production Build)

1. Create production build:
```bash
cd client
npm run build
```

2. Serve the build folder:
```bash
# Using serve (install globally: npm install -g serve)
serve -s build -l 3000
```

Or configure your backend to serve the React build:
- Copy `client/build` contents to `server/static`
- Modify Flask to serve static files

---

## Deploy to Render (Recommended - Free Tier Available)

Render provides free hosting for both backend and frontend.

### Backend Deployment

1. Create `render.yaml` in project root (already created below)
2. Push your code to GitHub
3. Go to [render.com](https://render.com) and sign up
4. Click "New +" → "Blueprint"
5. Connect your GitHub repository
6. Render will automatically deploy using the `render.yaml` configuration

### Frontend Deployment

Option 1: Static Site on Render
1. In Render Dashboard, click "New +" → "Static Site"
2. Connect your repository
3. Build Command: `cd client && npm install && npm run build`
4. Publish Directory: `client/build`

Option 2: Deploy to Netlify/Vercel (easier for React)
- See sections below

---

## Deploy to Railway (Easy & Free Tier)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects your setup
6. Add environment variables if needed
7. Deploy!

Configuration files (`railway.json`) already included.

---

## Deploy to Netlify (Frontend Only - Best for React)

1. Build your frontend:
```bash
cd client
npm run build
```

2. Go to [netlify.com](https://netlify.com)
3. Drag and drop the `client/build` folder
4. Or connect GitHub for continuous deployment

**Environment Variable:**
Add in Netlify dashboard:
```
REACT_APP_API_URL=https://your-backend-url.com
```

---

## Deploy to Vercel (Frontend Only - Alternative)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd client
vercel
```

Or use Vercel's GitHub integration for auto-deployment.

---

## Deploy to Heroku

### Backend

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app:
```bash
cd server
heroku create your-app-name-backend
```

4. Add `Procfile` (already created):
```
web: gunicorn wsgi:app
```

5. Deploy:
```bash
git push heroku main
```

### Frontend

1. Create separate Heroku app:
```bash
cd client
heroku create your-app-name-frontend
```

2. Add buildpack:
```bash
heroku buildpacks:set mars/create-react-app
```

3. Deploy:
```bash
git push heroku main
```

---

## Deploy to Cloud Providers (AWS/Azure/GCP)

### AWS EC2

1. Launch Ubuntu EC2 instance
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip nodejs npm nginx
```

4. Clone repository and setup:
```bash
git clone your-repo
cd mango-pesticide-detector

# Backend
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# Frontend
cd ../client
npm install
npm run build
```

5. Configure Nginx as reverse proxy (see nginx config below)

### Docker Deployment (Any Platform)

Use the provided Docker configuration:
```bash
docker-compose up -d
```

---

## Environment Variables

### Backend (.env)
```
FLASK_ENV=production
CORS_ORIGINS=https://your-frontend-url.com
```

### Frontend (.env.production)
```
REACT_APP_API_URL=https://your-backend-url.com/api
```

---

## Important Notes

1. **Model Files**: 
   - Model files (`.h5`, `.pkl`) are large
   - Either include them in repo with Git LFS, or
   - Upload them manually to your server after deployment
   - Or use cloud storage (S3, Google Cloud Storage)

2. **CORS Configuration**:
   - Update `server/app.py` with your frontend URL
   - Current: `CORS(app)` allows all origins (development only)
   - Production: `CORS(app, origins=["https://your-frontend.com"])`

3. **Database** (if needed in future):
   - Current app doesn't use database
   - If you add one, use PostgreSQL/MySQL on production

4. **SSL/HTTPS**:
   - Most platforms (Render, Vercel, Netlify) provide free SSL
   - For custom servers, use Let's Encrypt (free)

---

## Quick Start Recommendation

**For Students/Learning (Free & Easy):**
- **Backend**: Render (free tier)
- **Frontend**: Netlify or Vercel (free tier)
- **Total Cost**: $0

**Steps:**
1. Push code to GitHub
2. Deploy backend on Render (see render.yaml)
3. Deploy frontend on Netlify (drag & drop build folder)
4. Update frontend API URL to point to Render backend
5. Done! 🎉

---

## Testing Deployment

After deployment, test with:
```bash
# Backend health check
curl https://your-backend-url.com/api/health

# Frontend
Open https://your-frontend-url.com in browser
```

---

## Troubleshooting

**Backend won't start:**
- Check logs: `heroku logs --tail` or Render logs
- Ensure all dependencies in requirements.txt
- Verify model files are present

**Frontend can't reach backend:**
- Check CORS settings
- Verify API URL environment variable
- Check network/firewall rules

**Models not found:**
- Ensure model files are uploaded
- Check file paths in detect.py
- Verify directory structure

---

Need help? Check the platform-specific documentation or create an issue on GitHub.
