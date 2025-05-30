# Tunnelgrid.ai Development Guide

## 🎯 For Product Managers & Non-Developers

This guide explains the codebase in simple terms for non-developers who want to understand how the AI brand analysis platform works.

## 📋 What This Application Does

**Tunnelgrid.ai** is a web application that helps businesses analyze brands using artificial intelligence. Here's what it does:

1. **Brand Search**: Users can search for any brand (like "Apple" or "Nike")
2. **AI Analysis**: The system uses AI to analyze the brand and understand its characteristics
3. **Persona Generation**: Creates different customer personas (types of customers) for the brand
4. **Question Generation**: Creates specific questions for each persona to help with market research
5. **Topic Generation**: Suggests relevant topics for content marketing

## 🏗️ How It's Built (Architecture)

The application has three main parts:

### 1. Frontend (User Interface)
- **Technology**: React with TypeScript
- **What it does**: This is what users see and interact with in their web browser
- **Location**: `frontend/` directory
- **Runs on**: http://localhost:5173

### 2. Backend (Business Logic)
- **Technology**: Python with FastAPI
- **What it does**: Handles all the business logic, AI processing, and data management
- **Location**: `backend/` directory  
- **Runs on**: http://localhost:8000

### 3. External Services
- **Logo.dev**: Provides brand information and logos
- **GroqCloud**: AI service that generates personas, questions, and topics
- **Supabase**: Database that stores all the data

## 📁 Project Structure Explained

```
tunnelgrid-ai/
├── frontend/                 # User interface (React app)
│   ├── src/
│   │   ├── components/       # Reusable UI pieces (buttons, forms, etc.)
│   │   ├── services/         # Code that talks to the backend
│   │   ├── hooks/            # Reusable logic
│   │   ├── pages/            # Different screens/pages
│   │   ├── types/            # Data structure definitions
│   │   └── contexts/         # Global state management
│   └── package.json          # Lists what libraries are needed
│
├── backend/                  # Server logic (Python app)
│   ├── app/
│   │   ├── core/             # Basic functionality (config, database)
│   │   ├── models/           # Data structure definitions
│   │   ├── routes/           # API endpoints (like /api/brands)
│   │   └── main.py           # Main server file
│   └── requirements.txt      # Lists what Python libraries are needed
│
├── tests/                    # Automated tests
│   ├── backend/              # Tests for server logic
│   ├── frontend/             # Tests for user interface
│   ├── integration/          # Tests for full system
│   └── api/                  # Tests for API endpoints
│
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── .env.example              # Template for configuration
```

## 🔄 How Data Flows Through the System

1. **User Action**: User searches for a brand in the frontend
2. **API Call**: Frontend sends request to backend API
3. **External API**: Backend calls Logo.dev to get brand information
4. **AI Processing**: Backend sends brand data to GroqCloud for AI analysis
5. **Database**: Results are saved to Supabase database
6. **Response**: Backend sends results back to frontend
7. **Display**: Frontend shows the results to the user

```
User Input → Frontend → Backend API → External APIs → Database → Backend → Frontend → User Display
```

## 🛠️ Key Files Explained

### Backend Key Files

- **`backend/app/main.py`**: The main server file that starts everything and routes requests
- **`backend/app/routes/brands.py`**: Handles brand search and analysis requests
- **`backend/app/routes/personas.py`**: Handles persona generation requests
- **`backend/app/routes/questions.py`**: Handles question generation requests
- **`backend/app/routes/topics.py`**: Handles topic generation requests
- **`backend/app/core/config.py`**: Configuration settings for the app
- **`backend/app/core/database.py`**: Database connection and operations
- **`backend/app/models/`**: Defines the structure of data (brands, personas, etc.)

### Frontend Key Files

- **`frontend/src/App.tsx`**: Main application component that sets up the app
- **`frontend/src/components/`**: Reusable UI components (buttons, forms, cards)
- **`frontend/src/services/`**: Code that communicates with backend APIs
- **`frontend/src/pages/`**: Different screens (home, search results, etc.)
- **`frontend/src/hooks/`**: Reusable logic for data fetching and state management
- **`frontend/package.json`**: Lists all the frontend libraries and scripts

## 🔧 Development Workflow

### For Making Changes

1. **Understand the Feature**: What exactly needs to be changed?
2. **Identify Location**: Is it a frontend (UI) or backend (logic) change?
3. **Make Changes**: Edit the appropriate files
4. **Test**: Run tests to make sure nothing broke
5. **Deploy**: Push changes to production

### Common Change Types

- **UI Changes**: Edit files in `frontend/src/components/` or `frontend/src/pages/`
- **API Changes**: Edit files in `backend/app/routes/`
- **Database Changes**: Update models in `backend/app/models/`
- **Configuration**: Edit `.env` files or `backend/app/core/config.py`
- **Business Logic**: Edit the appropriate route or service files

## 🧪 Testing Strategy

The project has different types of tests organized in the `tests/` directory:

- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test how different parts work together
- **API Tests**: Test the backend endpoints directly
- **Frontend Tests**: Test the user interface components

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run only backend tests
python run_tests.py --backend

# Run with coverage report
python run_tests.py --coverage
```

## 🚀 Deployment Process

1. **Development**: Make changes locally on your computer
2. **Testing**: Run all tests to ensure quality
3. **Staging**: Deploy to a test environment for final verification
4. **Production**: Deploy to live environment for users

## 📊 Monitoring & Analytics

Key metrics to track:
- **API Response Times**: How fast the backend responds to requests
- **Error Rates**: How often things go wrong
- **User Engagement**: How users interact with the platform
- **AI Quality**: How good the generated content is
- **Database Performance**: How efficiently data is stored and retrieved

## 🔍 Troubleshooting Common Issues

### Backend Issues
- **Server won't start**: Check if all environment variables are set in `.env` file
- **API errors**: Check logs in `backend/questions_debug.log`
- **Database issues**: Verify Supabase connection and credentials
- **AI generation fails**: Check GroqCloud API key and rate limits

### Frontend Issues
- **Page won't load**: Check if backend is running on port 8000
- **API calls failing**: Check network tab in browser developer tools
- **Build errors**: Check for missing dependencies in `package.json`
- **Styling issues**: Check Tailwind CSS configuration

## 📈 Performance Considerations

- **AI Calls**: GroqCloud calls can take 5-10 seconds, so we show loading states
- **Database Queries**: Optimize for large datasets using proper indexing
- **Frontend Loading**: Use loading states and skeleton screens for better UX
- **Caching**: Cache frequently requested data to improve response times
- **Image Loading**: Optimize brand logos and images for fast loading

## 🔐 Security Considerations

- **API Keys**: Never expose in frontend code, always keep in backend `.env` files
- **Environment Variables**: Keep sensitive data in `.env` files that are not committed to git
- **Database Access**: Use proper authentication and row-level security
- **CORS**: Configure properly for frontend-backend communication
- **Rate Limiting**: Implemented to prevent API abuse

## 📝 Adding New Features

### Adding a New API Endpoint

1. Create new route file in `backend/app/routes/` (e.g., `insights.py`)
2. Add data models in `backend/app/models/` if needed
3. Update `backend/app/main.py` to include the new route
4. Write tests in `tests/backend/` or `tests/api/`
5. Update frontend service in `frontend/src/services/` to call the endpoint
6. Create UI components in `frontend/src/components/` to display the data

### Adding a New UI Component

1. Create component file in `frontend/src/components/` (e.g., `InsightCard.tsx`)
2. Add any needed styling using Tailwind CSS classes
3. Import and use in appropriate pages in `frontend/src/pages/`
4. Write tests in `tests/frontend/`
5. Update TypeScript types if needed in `frontend/src/types/`

## 🤝 Working with the Team

- **Code Reviews**: All changes should be reviewed by another developer
- **Documentation**: Update docs when making changes that affect user workflows
- **Communication**: Discuss major changes before implementing them
- **Version Control**: Use meaningful commit messages and branch names
- **Testing**: Always run tests before submitting changes

## 🔧 Environment Setup

### Development Environment
- **Backend**: Python 3.9+, virtual environment, FastAPI
- **Frontend**: Node.js 18+, npm, React with TypeScript
- **Database**: Supabase (PostgreSQL-based)
- **AI Services**: GroqCloud API
- **Brand Data**: Logo.dev API

### Required API Keys
- **LOGODEV_SECRET_KEY**: For brand data and logos
- **GROQ_API_KEY**: For AI processing (personas, questions, topics)
- **SUPABASE_URL** and **SUPABASE_SERVICE_ROLE_KEY**: For database operations

## 📚 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/ - Python web framework
- **React**: https://reactjs.org/ - Frontend JavaScript library
- **TypeScript**: https://www.typescriptlang.org/ - Type-safe JavaScript
- **Tailwind CSS**: https://tailwindcss.com/ - Utility-first CSS framework
- **Supabase**: https://supabase.com/ - Open source Firebase alternative

This guide should help you understand how the codebase works and how to make changes effectively! 