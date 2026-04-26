# 💰 AI Expense Tracker

A full-stack web application for tracking expenses, managing budgets, 
and getting AI-powered spending insights.

## 🚀 Features
- JWT-based authentication (register, login, refresh tokens)
- Expense management (add, edit, delete, categorize)
- Budget tracking with real-time alerts
- Monthly dashboard with charts
- AI-powered spending insights via OpenAI GPT-4o-mini

## 🛠️ Tech Stack

**Frontend:**
- React 18 + Vite
- Tailwind CSS + shadcn/ui
- Zustand + TanStack Query
- Recharts

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy 2.0 + Alembic
- SQLite (dev) / MySQL (prod)
- JWT Authentication

**AI:**
- OpenAI GPT-4o-mini (primary)
- Anthropic Claude Haiku (fallback)

## 📦 Setup

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## 📸 Screenshots
Coming soon

## 📄 License
MIT