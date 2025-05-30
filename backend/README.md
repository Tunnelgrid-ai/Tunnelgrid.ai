# AI Brand Analysis Backend

## Clean Architecture (After Cleanup)

This backend now has a clean, single-purpose FastAPI setup with no conflicting servers.

### Server Configuration

1. **Brand Search API** (`main.py`)
   - **Purpose:** Logo.dev brand search functionality 
   - **Host:** 127.0.0.1 (localhost)
   - **Port:** 5000 (matches frontend proxy)
   - **Endpoints:** `/api/brand-search`, `/api/insert-brand`, `/api/brand-llama`, `/api/update-brand-product`

2. **Topics API** (`app/main.py`) 
   - **Purpose:** GroqCloud AI topics generation
   - **Host:** 127.0.0.1 (localhost)
   - **Port:** 8000
   - **Endpoints:** `/api/topics/generate`, `/api/topics/fallback`, `/api/topics/health`

### ✅ Removed Conflicting Components

- ❌ `app.py` (Gradio app)
- ❌ `api.py` (Brandfetch API)  
- ❌ `package.json` (Node.js config)
- ❌ `routes/topics.js` (Node.js routes)
- ❌ `env.example` (inauthentic placeholder file)

### Running the Servers

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Brand Search API (Port 5000):**
   ```bash
   python main.py
   ```

3. **Start Topics API (Port 8000) - In separate terminal:**
   ```bash
   cd app && python main.py
   ```

### Environment Variables Required

Your hidden `.env` files should contain:
```
LOGODEV_SECRET_KEY=your_actual_logo_dev_api_key
GROQ_API_KEY=your_actual_groq_api_key
SUPABASE_URL=your_actual_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_actual_supabase_key
```

**Note:** Both backend and frontend directories should have their own `.env` files with the appropriate keys for each service.

### Testing

- **Brand Search:** `http://127.0.0.1:5000/api/brand-search?q=apple`
- **Topics API:** `http://127.0.0.1:8000/api/topics/health`
- **Frontend:** Runs on port 8080 and proxies to 127.0.0.1:5000

### Host Configuration Fix

Changed host from `0.0.0.0` to `127.0.0.1` to resolve potential connection issues. This ensures:
- More reliable local development
- Better compatibility with Windows networking
- Clearer localhost-only access

This should resolve all 500 errors and server conflicts! 