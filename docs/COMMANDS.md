# Tunnelgrid.ai Command Reference

## 🚀 Quick Start Commands

### Initial Setup (Run Once)

```bash
# 1. Clone the repository
git clone https://github.com/aruniyer88/Tunnelgrid.ai.git
cd Tunnelgrid.ai

# 2. Run automated setup
python setup.py
```

### Manual Setup (Alternative)

```bash
# Backend setup
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Frontend setup (in new terminal)
cd frontend
npm install
```

## 🏃‍♂️ Running the Application

### Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start the server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Backend will be available at:**
- API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Start Frontend Server

```bash
# Navigate to frontend directory (in new terminal)
cd frontend

# Start development server
npm run dev
```

**Frontend will be available at:**
- Application: http://localhost:5173

## 🧪 Testing Commands

### Run All Tests

```bash
# Using the test runner
python run_tests.py

# Or using pytest directly
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Backend tests only
python run_tests.py --backend
# OR
pytest tests/backend/ -v

# Frontend tests only
python run_tests.py --frontend
# OR
pytest tests/frontend/ -v

# Integration tests only
python run_tests.py --integration
# OR
pytest tests/integration/ -v

# API tests only
pytest tests/api/ -v
```

### Test with Coverage

```bash
# Generate coverage report
pytest --cov=backend/app tests/ --cov-report=html --cov-report=term-missing

# View coverage report
# Open htmlcov/index.html in your browser
```

### Run Specific Test Files

```bash
# Test a specific file
pytest tests/backend/test_brands.py -v

# Test a specific function
pytest tests/backend/test_brands.py::test_search_brands -v

# Run tests with specific markers
pytest -m "not slow" tests/
```

## 🔧 Development Commands

### Backend Development

```bash
# Start with auto-reload (development)
uvicorn app.main:app --reload

# Start with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Check Python code style
flake8 backend/app/

# Format Python code
black backend/app/

# Type checking
mypy backend/app/
```

### Frontend Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Fix linting issues
npm run lint --fix

# Type checking
npm run type-check
```

## 🐛 Debugging Commands

### Backend Debugging

```bash
# Start with debug logging
DEBUG=True python -m uvicorn app.main:app --reload

# Check logs
tail -f backend/questions_debug.log

# Test specific API endpoints
curl http://localhost:8000/health
curl "http://localhost:8000/api/brands/search?q=apple"
```

### Frontend Debugging

```bash
# Start with verbose output
npm run dev -- --debug

# Check bundle size
npm run build -- --analyze

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🔍 Health Check Commands

### Backend Health Checks

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check specific services
curl http://localhost:8000/api/topics/health

# Test database connection
curl http://localhost:8000/test-supabase
```

### Frontend Health Checks

```bash
# Check if frontend is accessible
curl http://localhost:5173

# Check build status
npm run build
```

## 📦 Package Management

### Backend Dependencies

```bash
# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Update all packages
pip list --outdated
pip install --upgrade package_name
```

### Frontend Dependencies

```bash
# Install new package
npm install package_name

# Install dev dependency
npm install --save-dev package_name

# Update packages
npm update

# Check for outdated packages
npm outdated

# Audit for vulnerabilities
npm audit
npm audit fix
```

## 🚀 Production Commands

### Build for Production

```bash
# Backend - no special build needed
# Just ensure all dependencies are installed

# Frontend
cd frontend
npm run build
```

### Environment Management

```bash
# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Check environment variables
# Backend
cd backend && python -c "from app.core.config import settings; print(settings)"

# Frontend
cd frontend && npm run env-check
```

## 🔄 Database Commands

### Supabase Operations

```bash
# Test database connection
python -c "
from backend.app.core.database import test_database_connection
print('Connected:', test_database_connection())
"

# Run database migrations (if any)
# This would depend on your specific migration setup
```

## 📊 Monitoring Commands

### Performance Monitoring

```bash
# Monitor backend performance
# Add monitoring tools as needed

# Check memory usage
ps aux | grep uvicorn

# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173
```

## 🧹 Cleanup Commands

### Clean Build Artifacts

```bash
# Backend cleanup
find . -type d -name "__pycache__" -delete
find . -name "*.pyc" -delete

# Frontend cleanup
cd frontend
rm -rf dist/
rm -rf node_modules/
npm install
```

### Reset Environment

```bash
# Reset backend virtual environment
cd backend
rm -rf venv/
python -m venv venv
# Activate and install requirements again

# Reset frontend dependencies
cd frontend
rm -rf node_modules/ package-lock.json
npm install
```

## 🆘 Troubleshooting Commands

### Common Issues

```bash
# Port already in use
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Permission issues (macOS/Linux)
sudo chown -R $USER:$USER .

# Python path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

### Reset Everything

```bash
# Nuclear option - reset everything
rm -rf backend/venv/
rm -rf frontend/node_modules/
rm -rf frontend/dist/
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf htmlcov/

# Then run setup again
python setup.py
```

## 📝 Useful Aliases

Add these to your shell profile for convenience:

```bash
# Backend aliases
alias be-start="cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
alias be-test="cd backend && source venv/bin/activate && pytest tests/ -v"

# Frontend aliases
alias fe-start="cd frontend && npm run dev"
alias fe-build="cd frontend && npm run build"
alias fe-test="cd frontend && npm test"

# Combined aliases
alias start-all="be-start & fe-start"
alias test-all="python run_tests.py"
```

This command reference should help you navigate all the common tasks for developing and maintaining Tunnelgrid.ai! 