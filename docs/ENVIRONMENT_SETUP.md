# Tunnelgrid.ai Environment Setup Guide

## 🎯 Quick Setup (Recommended)

The fastest way to get started is using the automated setup script:

```bash
# Clone and setup
git clone https://github.com/aruniyer88/Tunnelgrid.ai.git
cd Tunnelgrid.ai
python setup.py
```

This script will:
- ✅ Check prerequisites (Python, Node.js, npm)
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Create environment file templates
- ✅ Provide next steps guidance

## 🔧 Manual Setup

If you prefer manual setup or need to troubleshoot:

### 1. Prerequisites

**Required Software:**
- **Python 3.9+** - [Download Python](https://python.org)
- **Node.js 18+** - [Download Node.js](https://nodejs.org)
- **Git** - [Download Git](https://git-scm.com)

**Required API Keys:**
- **Logo.dev API Key** - [Get API Key](https://logo.dev)
- **GroqCloud API Key** - [Get API Key](https://console.groq.com)
- **Supabase Keys** - [Create Project](https://supabase.com)

### 2. Clone Repository

```bash
git clone https://github.com/aruniyer88/Tunnelgrid.ai.git
cd Tunnelgrid.ai
```

### 3. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Environment Configuration

#### Backend Environment (.env)

Create `backend/.env`:

```env
# API Keys
LOGODEV_SECRET_KEY=your_logo_dev_api_key_here
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Server Configuration
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
DEBUG=True
```

#### Frontend Environment (.env)

Create `frontend/.env`:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

## 🔑 API Keys Setup

### Logo.dev API Key

1. Go to [Logo.dev](https://logo.dev)
2. Sign up for an account
3. Navigate to API section
4. Generate an API key
5. Add to `backend/.env` as `LOGODEV_SECRET_KEY`

### GroqCloud API Key

1. Go to [GroqCloud Console](https://console.groq.com)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Add to `backend/.env` as `GROQ_API_KEY`

### Supabase Setup

1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Get your project URL and keys from Settings > API
4. Add to both `backend/.env` and `frontend/.env`

**Required Supabase Tables:**

```sql
-- Brand table
CREATE TABLE brand (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    brand_description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Persona table
CREATE TABLE persona (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    age_range VARCHAR(50),
    income_level VARCHAR(50),
    interests TEXT[],
    brand_id INTEGER REFERENCES brand(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Question table
CREATE TABLE question (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    persona_id INTEGER REFERENCES persona(id),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product table
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    brand_id INTEGER REFERENCES brand(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit table
CREATE TABLE audit (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Backend URLs:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Start Frontend

```bash
cd frontend
npm run dev
```

**Frontend URL:**
- App: http://localhost:5173

## ✅ Verification

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Test brand search (requires Logo.dev API key)
curl "http://localhost:8000/api/brands/search?q=apple"
```

### Test Frontend

1. Open http://localhost:5173 in your browser
2. Search for a brand (e.g., "Apple")
3. Generate personas and questions

## 🧪 Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --backend
python run_tests.py --frontend
python run_tests.py --integration

# Run with coverage
python run_tests.py --coverage
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Python Virtual Environment Issues

**Error**: `venv\Scripts\activate` not found

**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
```

#### 2. Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

#### 3. API Key Issues

**Error**: `Logo.dev API key not configured`

**Solution**:
1. Verify `.env` file exists in `backend/` directory
2. Check that `LOGODEV_SECRET_KEY` is set correctly
3. Restart the backend server

#### 4. Database Connection Issues

**Error**: `Database connection failed`

**Solution**:
1. Verify Supabase URL and keys in `.env`
2. Check if Supabase project is active
3. Verify tables are created in Supabase

#### 5. Frontend Build Issues

**Error**: `Module not found` or similar

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Environment Variables Debug

If environment variables aren't loading:

```bash
# Check if .env file exists
ls -la backend/.env
ls -la frontend/.env

# Test environment loading
cd backend
python -c "
from app.core.config import settings
print(f'Logodev configured: {settings.has_logodev_config}')
print(f'Groq configured: {settings.has_groq_config}')
print(f'Supabase configured: {settings.has_supabase_config}')
"
```

## 🔄 Development Workflow

### Daily Development

1. **Start Development**:
   ```bash
   # Terminal 1: Backend
   cd backend && venv\Scripts\activate && uvicorn app.main:app --reload
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. **Make Changes**: Edit code in your preferred editor

3. **Test Changes**: Run relevant tests
   ```bash
   python run_tests.py --backend  # After backend changes
   npm run lint                   # After frontend changes
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push
   ```

### Code Quality

```bash
# Backend
cd backend
python -m pytest tests/ -v
python -m flake8 app/  # If flake8 is installed

# Frontend
cd frontend
npm run lint
npm run type-check
```

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://reactjs.org/
- **Supabase Documentation**: https://supabase.com/docs
- **Logo.dev API Docs**: https://logo.dev/docs
- **GroqCloud Docs**: https://console.groq.com/docs

## 🆘 Getting Help

1. **Check Documentation**: Review relevant docs files
2. **Check Issues**: Look at existing GitHub issues
3. **Debug Mode**: Run with DEBUG=True for detailed logs
4. **Community**: Join our Discord/Slack for help

This setup guide should get you up and running with Tunnelgrid.ai development environment! 