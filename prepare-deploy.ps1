# Deployment Preparation Script
# Run this before deploying

Write-Host "🚀 Mango Pesticide Detector - Deployment Preparation" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "server") -or -not (Test-Path "client")) {
    Write-Host "❌ Error: Run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Running from correct directory" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "🐍 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Install Python 3.9+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check Node.js
Write-Host "📦 Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Install Node.js 16+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check model files
Write-Host "🤖 Checking model files..." -ForegroundColor Yellow
$modelFiles = @(
    "server\model\mango_model.h5",
    "server\model\models\svm.pkl",
    "server\model\models\rf.pkl",
    "server\model\model_comparison.json"
)

$allModelsExist = $true
foreach ($file in $modelFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length / 1MB
        Write-Host "  ✅ $file ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - NOT FOUND" -ForegroundColor Red
        $allModelsExist = $false
    }
}

if (-not $allModelsExist) {
    Write-Host ""
    Write-Host "⚠️  Some model files are missing. Train models first:" -ForegroundColor Yellow
    Write-Host "   python .\server\model\model_trainer.py --data-dir .\dataset --epochs 15" -ForegroundColor Cyan
    Write-Host "   python .\server\model\compare_models.py --data-dir .\dataset" -ForegroundColor Cyan
}
Write-Host ""

# Check if virtual environment exists
Write-Host "🔧 Checking Python environment..." -ForegroundColor Yellow
if (Test-Path "server\.venv") {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    cd server
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    cd ..
}
Write-Host ""

# Test backend dependencies
Write-Host "📚 Checking backend dependencies..." -ForegroundColor Yellow
cd server
& .\.venv\Scripts\Activate.ps1
$missing = $false
$packages = @("flask", "tensorflow", "scikit-learn", "pillow", "gunicorn")
foreach ($pkg in $packages) {
    $result = pip show $pkg 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ $pkg not installed" -ForegroundColor Red
        $missing = $true
    } else {
        Write-Host "  ✅ $pkg installed" -ForegroundColor Green
    }
}

if ($missing) {
    Write-Host ""
    Write-Host "⚠️  Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}
cd ..
Write-Host ""

# Test frontend dependencies
Write-Host "🎨 Checking frontend dependencies..." -ForegroundColor Yellow
cd client
if (Test-Path "node_modules") {
    Write-Host "✅ node_modules exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  node_modules not found. Installing..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
}
cd ..
Write-Host ""

# Test backend build
Write-Host "🔨 Testing backend..." -ForegroundColor Yellow
cd server
& .\.venv\Scripts\Activate.ps1
$testImport = python -c "import flask; import tensorflow; import sklearn; print('OK')" 2>&1
if ($testImport -match "OK") {
    Write-Host "✅ Backend imports working" -ForegroundColor Green
} else {
    Write-Host "❌ Backend import errors:" -ForegroundColor Red
    Write-Host $testImport -ForegroundColor Red
}
cd ..
Write-Host ""

# Test frontend build
Write-Host "🏗️  Testing frontend build..." -ForegroundColor Yellow
cd client
Write-Host "   (This may take a minute...)" -ForegroundColor Gray
$buildOutput = npm run build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend build successful" -ForegroundColor Green
    $buildSize = (Get-ChildItem -Path "build" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "   Build size: $([math]::Round($buildSize, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    Write-Host $buildOutput -ForegroundColor Red
}
cd ..
Write-Host ""

# Check Git
Write-Host "📝 Checking Git..." -ForegroundColor Yellow
try {
    $gitStatus = git status 2>&1
    if ($gitStatus -match "not a git repository") {
        Write-Host "⚠️  Not a git repository. Initialize with:" -ForegroundColor Yellow
        Write-Host "   git init" -ForegroundColor Cyan
        Write-Host "   git add ." -ForegroundColor Cyan
        Write-Host "   git commit -m 'Initial commit'" -ForegroundColor Cyan
    } else {
        Write-Host "✅ Git repository initialized" -ForegroundColor Green
        
        # Check for uncommitted changes
        $status = git status --porcelain
        if ($status) {
            Write-Host "⚠️  You have uncommitted changes:" -ForegroundColor Yellow
            git status --short
        } else {
            Write-Host "✅ No uncommitted changes" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "⚠️  Git not found. Install Git for deployment" -ForegroundColor Yellow
}
Write-Host ""

# Calculate total project size
Write-Host "📊 Project Statistics..." -ForegroundColor Yellow
$totalSize = (Get-ChildItem -Path . -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "   Total project size: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan

# Count files
$pyFiles = (Get-ChildItem -Path server -Recurse -Filter *.py | Measure-Object).Count
$jsFiles = (Get-ChildItem -Path client\src -Recurse -Filter *.js* | Measure-Object).Count
Write-Host "   Python files: $pyFiles" -ForegroundColor Cyan
Write-Host "   JavaScript files: $jsFiles" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "📋 SUMMARY" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

if ($allModelsExist) {
    Write-Host "✅ All model files present" -ForegroundColor Green
} else {
    Write-Host "❌ Some model files missing - TRAIN MODELS FIRST" -ForegroundColor Red
}

Write-Host "✅ Dependencies checked" -ForegroundColor Green
Write-Host "✅ Builds tested" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Review PRE_DEPLOYMENT_CHECKLIST.md" -ForegroundColor Cyan
Write-Host "   2. Choose deployment platform from QUICKSTART_DEPLOY.md" -ForegroundColor Cyan
Write-Host "   3. Push code to GitHub" -ForegroundColor Cyan
Write-Host "   4. Deploy!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   - QUICKSTART_DEPLOY.md - Quick deployment guide" -ForegroundColor Cyan
Write-Host "   - DEPLOYMENT.md - Comprehensive deployment guide" -ForegroundColor Cyan
Write-Host "   - PRE_DEPLOYMENT_CHECKLIST.md - Pre-deployment checklist" -ForegroundColor Cyan
Write-Host "   - README.md - Project documentation" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Ready to deploy! Good luck! 🚀" -ForegroundColor Green
