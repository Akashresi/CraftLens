# CraftLens 2.0 Production Deployment Guide

## 1. Prerequisites
- Docker Engine 24.0+ & Docker Compose v2.20+
- Python 3.11+
- Node.js 20+ & pnpm 9+
- PostgreSQL 16 with `pgvector` extension
- Redis 7+

---

## 2. Environment Configuration
Copy `.env.example` to `.env` and configure production secrets:
```bash
cp .env.example .env
```
Ensure the following variables are customized for production:
- `SECRET_KEY`: Generate a 64-character random hex string (`openssl rand -hex 32`)
- `APP_ENV`: Set to `production`
- `DATABASE_URL`: `postgresql+psycopg2://<user>:<password>@<db-host>:5432/<db-name>`
- `REDIS_URL`: `redis://<redis-host>:6379/0`
- `GEMINI_API_KEY`: API key for Gemini LLM cataloging

---

## 3. Running with Docker Compose (Recommended)
Launch the unified cluster:
```bash
docker compose up -d --build
```

### Healthcheck Verification:
- Backend API: `curl -f http://localhost:8000/api/v1/health`
- Interactive OpenAPI Docs: `http://localhost:8000/api/v1/docs`
- Buyer Marketplace: `http://localhost:3000`
- Administrator Portal: `http://localhost:3001`

---

## 4. Database Migrations & Initial Seeding
When running standalone without Docker:
```bash
# Apply Alembic database migrations
cd backend
python -m alembic upgrade head

# Seed initial roles, craft categories, and GI origins
python app/db/init_db.py
```

---

## 5. Local Development Execution

### FastAPI Backend
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Buyer Web & Artisan Portal
```bash
cd buyer-web
npm install
npm run dev
```

### Administrator Portal
```bash
cd admin-web
npm install
npm run dev
```

### React Native Mobile Application
```bash
cd mobile
npm install
npx expo start
```
