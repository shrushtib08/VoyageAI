# VoyageAI Local Setup & Deployment Guide

This guide walks you through setting up and running **VoyageAI** locally or in production.

---

## 1. Prerequisites

- **Python**: Version 3.10+ (tested on Python 3.11.9)
- **Node.js**: Version 18+ (tested on Node.js v24.11.0)
- **Database**: PostgreSQL (recommended for production) or SQLite (supported out-of-the-box for local dev)

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` in the project root:

```bash
cp .env.example .env
```

### Key Configurations:

```ini
# LLM Provider (Groq)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# External APIs (Optional - Resilient Fallbacks Active)
TAVILY_API_KEY=tvly-your_tavily_key
AVIATIONSTACK_API_KEY=your_aviationstack_key
OPENWEATHER_API_KEY=your_openweather_key

# Database
# For SQLite (default):
DATABASE_URL=sqlite:///./voyageai.db
# For PostgreSQL:
# DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/voyageai

# Security & Secret Key
SECRET_KEY=voyageai_super_secret_jwt_key_32_characters_long
```

---

## 3. Backend Setup

1. **Create and Activate Virtual Environment**:
   ```powershell
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run Database Migrations & Start Server**:
   ```powershell
   $env:PYTHONPATH = "backend"
   .\venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The backend will be live at: `http://localhost:8000`  
   Interactive API documentation: `http://localhost:8000/docs`

---

## 4. Frontend Setup

1. **Navigate to Frontend Directory**:
   ```bash
   cd frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```

   The web UI will be live at: `http://localhost:5173`

4. **Production Build**:
   ```bash
   npm run build
   ```

---

## 5. PostgreSQL Database Configuration (Optional)

If running PostgreSQL locally or via Docker:

1. **Start PostgreSQL Container**:
   ```bash
   docker run --name voyageai-postgres -e POSTGRES_DB=voyageai -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
   ```

2. **Update `.env`**:
   ```ini
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/voyageai
   ```

3. The application will automatically initialize all relational tables on startup via SQLAlchemy.

---

## 6. Running Automated Tests

Run the complete backend and agent orchestration test suite:

```powershell
$env:PYTHONPATH = "backend"
.\venv\Scripts\pytest backend/tests/test_backend.py -v
```
