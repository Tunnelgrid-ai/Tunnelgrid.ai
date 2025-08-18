# Tunnelgrid.ai - AI Brand Analysis Platform

## 🎯 Project Overview

Tunnelgrid.ai is an AI-powered brand analysis platform that helps businesses understand their brand positioning, generate customer personas, and create targeted marketing strategies.

### Key Features:
- **Brand Search & Analysis**: Search for brands and get AI-powered insights
- **Customer Personas**: Generate detailed customer personas based on brand characteristics
- **AI-Generated Questions**: Create persona-specific questions for market research
- **Topic Generation**: Generate relevant topics for content and marketing strategies

## 🏗️ Architecture

```
Frontend (React + TypeScript) 
    ↓
Backend API (FastAPI + Python)
    ↓
External APIs:
- Logo.dev (Brand data)
- GroqCloud (AI processing)
- Supabase (Database)
```

## 📁 Project Structure

```
tunnelgrid-ai/
├── frontend/                # React TypeScript frontend
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities
│   │   └── pages/          # Page components
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
│
├── backend/                # FastAPI backend
│   ├── app/               # Main application
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Data models
│   │   ├── routes/        # API endpoints
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
│
├── tests/                  # Integration tests
│   ├── backend/           # Backend-specific tests
│   ├── frontend/          # Frontend-specific tests
│   └── integration/       # Full-stack tests
│
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── .env.example           # Environment variables template
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- API Keys for:
  - Logo.dev
  - GroqCloud
  - Supabase

### Environment Setup

1. **Clone the repository**
```bash
git clone https://github.com/aruniyer88/Tunnelgrid.ai.git
cd Tunnelgrid.ai
```

2. **Set up environment variables**

Create `.env` files in both `frontend/` and `backend/` directories:

**backend/.env**
```env
# API Keys
LOGODEV_SECRET_KEY=your_logo_dev_api_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key

# Server Configuration
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
```

**frontend/.env**
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Backend Setup

1. **Create Python virtual environment**
```bash
cd backend
python -m venv venv
```

2. **Activate virtual environment**
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start the backend server**
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
python tests/integration/run_all_tests.py
```

## 📚 API Endpoints

### Core Endpoints

- **Brand Management**
  - `GET /api/brands/search?q={query}` - Search for brands
  - `POST /api/brands/` - Create a new brand
  - `POST /api/brands/analyze` - Analyze a brand with AI

- **Personas**
  - `GET /api/personas/` - Get all personas
  - `POST /api/personas/generate` - Generate personas for a brand

- **Questions**
  - `GET /api/questions/` - Get all questions
  - `POST /api/questions/generate` - Generate questions for personas

- **Topics**
  - `POST /api/topics/generate` - Generate topics for a brand

## 🛠️ Development Commands

### Backend
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Run specific test file
pytest tests/test_brands.py

# Check code coverage
pytest --cov=app tests/
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Backend: Change port in backend/.env
   - Frontend: Vite will automatically find an available port

2. **API Connection Issues**
   - Verify backend is running on http://localhost:8000
   - Check CORS settings in backend
   - Ensure frontend proxy is configured correctly

3. **Database Connection**
   - Verify Supabase credentials
   - Check if tables are created in Supabase

## 📊 Database Schema

### Key Tables
- `brand` - Brand information
- `product` - Products associated with brands
- `audit` - Audit logs
- `persona` - Customer personas
- `question` - Generated questions

## 🚀 Deployment

### Backend Deployment (e.g., on Render)
1. Set environment variables
2. Use `uvicorn app.main:app` as start command
3. Ensure port binding uses `PORT` env variable

### Frontend Deployment (e.g., on Vercel)
1. Set environment variables
2. Build command: `npm run build`
3. Output directory: `dist`

## 📝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## 📄 License

[Your License Here] 