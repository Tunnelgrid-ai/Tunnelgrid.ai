# Tunnelgrid.ai - AI-Powered Brand Analysis Platform

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/AI_Powered-FF6B6B?style=for-the-badge&logo=brain&logoColor=white" alt="AI Powered" />
</p>

## 🚀 Overview

Tunnelgrid.ai is an innovative AI-powered platform that helps businesses analyze their brand positioning, generate customer personas, and create targeted marketing strategies using advanced AI models.

### ✨ Key Features

- **🔍 Brand Search & Analysis**: Search for any brand and get comprehensive AI-powered insights
- **👥 Customer Personas**: Automatically generate detailed customer personas based on brand characteristics
- **❓ AI-Generated Questions**: Create persona-specific questions for targeted market research
- **📝 Topic Generation**: Generate relevant topics for content marketing and strategy
- **🎯 Real-time Analysis**: Get instant insights powered by GroqCloud AI

## 📚 Documentation

This project includes comprehensive documentation for developers and non-developers:

| Document | Description | Audience |
|----------|-------------|----------|
| **[📖 Development Guide](docs/DEVELOPMENT_GUIDE.md)** | Complete guide for understanding the codebase | Product Managers & Non-Developers |
| **[🚀 Environment Setup](docs/ENVIRONMENT_SETUP.md)** | Detailed setup instructions and troubleshooting | Developers |
| **[🧪 Testing Guide](docs/TESTING_GUIDE.md)** | Comprehensive testing strategy and examples | Developers |
| **[📡 API Reference](docs/API_REFERENCE.md)** | Complete API documentation with examples | Developers & Integrators |
| **[⚡ Commands Reference](docs/COMMANDS.md)** | All available commands for development | Developers |
| **[🏗️ Project Structure](PROJECT_STRUCTURE.md)** | Detailed project architecture overview | All Users |

## ⚡ Quick Start

### 1. Automated Setup (Recommended)

```bash
# Clone and setup everything automatically
git clone https://github.com/aruniyer88/Tunnelgrid.ai.git
cd Tunnelgrid.ai
python setup.py
```

### 2. Manual Setup

**Prerequisites**: Python 3.9+, Node.js 18+, Git

```bash
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Frontend setup (new terminal)
cd frontend
npm install
```

### 3. Environment Configuration

Create environment files with your API keys:

**Backend** (`backend/.env`):
```env
LOGODEV_SECRET_KEY=your_logo_dev_api_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
```

**Frontend** (`frontend/.env`):
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 4. Run the Application

**Backend** (Terminal 1):
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

**Access the application:**
- 🌐 **Frontend**: http://localhost:5173
- 🔗 **API Docs**: http://localhost:8000/docs
- 📊 **Health Check**: http://localhost:8000/health

## 🏗️ Architecture

```
┌─────────────────────────┐
│   React + TypeScript    │  Frontend (Port 5173)
│      (Vite + Tailwind)  │
└────────────┬────────────┘
             │ HTTP/REST
┌────────────▼────────────┐
│      FastAPI Backend    │  Backend (Port 8000)
│        (Python)         │
└────────────┬────────────┘
             │
    ┌────────┴────────┬──────────┐
    ▼                 ▼          ▼
┌─────────┐    ┌──────────┐  ┌──────────┐
│Logo.dev │    │GroqCloud │  │ Supabase │
│   API   │    │    AI    │  │    DB    │
└─────────┘    └──────────┘  └──────────┘
```

## 🧪 Testing

### Run All Tests

```bash
# Quick test runner
python run_tests.py

# Specific test categories
python run_tests.py --backend
python run_tests.py --frontend
python run_tests.py --integration
python run_tests.py --coverage
```

### Test Organization

```
tests/
├── backend/          # Backend Python tests
├── frontend/         # Frontend React tests
├── integration/      # Full-stack tests
├── api/              # API endpoint tests
└── unit/             # Unit tests
```

## 📊 Project Statistics

- **Backend**: Python FastAPI with async support
- **Frontend**: React 18+ with TypeScript and Tailwind CSS
- **Tests**: 14+ comprehensive test files covering all components
- **Documentation**: 6 detailed guides covering all aspects
- **API Endpoints**: 15+ REST endpoints for complete functionality
- **AI Integration**: GroqCloud for advanced AI processing

## 🛠️ Development Tools

### Useful Commands

```bash
# Development
python run_tests.py --backend     # Test backend changes
npm run lint                      # Check frontend code style
python run_tests.py --coverage    # Generate coverage reports

# Production
npm run build                     # Build frontend for production
uvicorn app.main:app --host 0.0.0.0 --port 8000  # Production server
```

### Code Quality Features

- ✅ **Comprehensive Testing**: Unit, integration, and API tests
- ✅ **Type Safety**: TypeScript frontend, Python type hints
- ✅ **Code Organization**: Clean architecture with separated concerns  
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Documentation**: Extensive docs for all user types
- ✅ **Environment Management**: Secure API key handling

## 🤖 AI Features

### Brand Analysis
- **Search Integration**: Logo.dev API for brand discovery
- **AI Descriptions**: GroqCloud-powered brand analysis
- **Product Detection**: Automatic product line identification

### Persona Generation
- **Custom Personas**: AI-generated customer personas
- **Demographic Data**: Age ranges, income levels, interests
- **Behavioral Insights**: Customer behavior analysis

### Content Generation
- **Market Research Questions**: Persona-specific questionnaires
- **Topic Suggestions**: Content marketing topic generation
- **Strategy Insights**: AI-powered marketing recommendations

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/brands/search` | GET | Search brands via Logo.dev |
| `/api/brands/analyze` | POST | AI brand analysis |
| `/api/personas/generate` | POST | Generate customer personas |
| `/api/questions/generate` | POST | Create research questions |
| `/api/topics/generate` | POST | Generate content topics |

> **See [API Reference](docs/API_REFERENCE.md) for complete documentation**

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | `netstat -ano \| findstr :8000` then `taskkill /PID <PID> /F` |
| API key errors | Check `.env` files in backend/ and frontend/ |
| Database connection | Verify Supabase credentials and table setup |
| Frontend build errors | `rm -rf node_modules && npm install` |

> **See [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md) for detailed troubleshooting**

## 📝 Contributing

1. **Read the docs**: Start with [Development Guide](docs/DEVELOPMENT_GUIDE.md)
2. **Set up environment**: Follow [Environment Setup](docs/ENVIRONMENT_SETUP.md)
3. **Write tests**: See [Testing Guide](docs/TESTING_GUIDE.md)
4. **Submit PR**: Include tests and documentation updates

### Development Workflow

```bash
# 1. Start development
python run_tests.py                    # Verify current state
git checkout -b feature/new-feature    # Create feature branch

# 2. Make changes
# Edit code...

# 3. Test changes
python run_tests.py --backend          # Test backend
npm run lint                           # Check frontend

# 4. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing Python web framework
- [React](https://reactjs.org/) for the frontend framework
- [Supabase](https://supabase.com/) for the database and authentication
- [GroqCloud](https://groq.com/) for AI processing
- [Logo.dev](https://logo.dev/) for brand data

---

<p align="center">
  <strong>Built with ❤️ for modern brand analysis</strong><br>
  Made by <a href="https://github.com/aruniyer88">aruniyer88</a>
</p>
