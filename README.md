# CraftLens 2.0 📸🎨

> **Complete AI-Powered Artisan Business Management and Global Marketplace Platform**  
> *Smart India Hackathon (SIH 2026) | Problem Statement: SIH26090*  
> *Theme: Heritage & Culture | Ministry of Social Justice and Empowerment (MoSJE)*

---

## 🌟 Executive Overview

**CraftLens 2.0** is an enterprise-grade digital business manager and global marketplace platform designed specifically for marginalized artisans, traditional craftspeople, handloom weavers, and self-help groups (SHGs).

By merging computer vision, multilingual generative AI, explainable dynamic pricing, and cryptographic provenance, CraftLens dismantles the digital divide, protects indigenous artisans from commercial exploitation, and establishes direct market linkages to retail and B2B buyers worldwide.

---

## 🏗️ Monorepo Architecture

```
CraftLens/
├── backend/                     # FastAPI Core Backend Service
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST APIs (Auth, Studio, Voice, Pricing, Marketplace, Orders, B2B, Heritage, Business, Compliance)
│   │   ├── core/                # Argon2id security, JWT, app config
│   │   ├── db/                  # Session management, seed engine
│   │   ├── models/              # Normalized SQLAlchemy 2.0 models (38+ tables)
│   │   ├── schemas/             # Pydantic v2 validation models
│   │   ├── services/            # Vision pipeline, Voice ASR/NLP, Pricing engine, Business manager, Heritage QR
│   │   └── main.py              # Application entrypoint & static mounts
│   ├── tests/                   # Automated Pytest test suite (100% pass rate)
│   ├── alembic/                 # Database schema migrations
│   ├── requirements.txt         # Production dependencies
│   └── Dockerfile
├── buyer-web/                   # Next.js 14 Web Marketplace & Artisan Portal
│   ├── src/app/                 # Catalog, Studio, Onboarding, Login, Register
│   ├── src/components/          # Navbar, Multilingual language switcher
│   └── tailwind.config.ts       # Artisan-Commerce design system tokens
├── admin-web/                   # Next.js 14 Administrator & Governance Portal
│   ├── src/                     # Moderation, verification, and analytics
│   └── tailwind.config.ts
├── mobile/                      # React Native Expo Mobile Application
│   ├── app/                     # Low-literacy screens (Language, Camera Studio, Voice creation)
│   ├── src/constants/           # Mobile design system tokens (#285C45, #F8F6F0)
│   ├── src/services/            # Offline-first SQLite draft synchronization
│   └── src/store/               # Zustand state management
├── docs/                        # Architecture, Design System, Database, Deployment specs
│   ├── ARCHITECTURE.md
│   ├── DESIGN_SYSTEM.md
│   ├── DATABASE_SCHEMA.md
│   └── DEPLOYMENT.md
├── docker-compose.yml           # Multi-container orchestration (Postgres, Redis, Backend, Frontends)
├── .github/workflows/ci.yml     # Automated CI/CD pipeline
└── .env.example                 # Comprehensive environment template
```

---

## 🎨 Artisan-Commerce Design System

Rooted in Indian craft aesthetics, avoiding harsh neons and generic corporate gradients:
- **Primary (`#285C45`)**: Deep Forest Green (Trust, heritage, stability)
- **Secondary (`#C47B52`)**: Warm Terracotta (Earthen craft, warmth, highlights)
- **Background (`#F8F6F0`)**: Warm Ivory (Prevents screen fatigue, editorial feel)
- **Surface (`#FFFFFF`)**: Pure White (Card containers, input fields)
- **Text (`#242B27`)**: Dark Charcoal (Accessible high-contrast typography)
- **Border (`#E8E5DC`)**: Natural Beige (Clean dividers and subtle outlines)

---

## 🚀 Getting Started

### 1. Setup Backend & Run Automated Tests
```bash
# Run the complete automated test suite across all 10 modules
python -m pytest backend/tests -v

# Initialize and seed the database with core roles, categories & GI origins
python backend/app/db/init_db.py

# Launch the FastAPI server with live Swagger documentation
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API Docs: `http://127.0.0.1:8000/api/v1/docs`*

### 2. Launch Buyer Web & Artisan Portal
```bash
cd buyer-web
npm install
npm run dev
```
*Web App: `http://localhost:3000`*

### 3. Launch Mobile Application
```bash
cd mobile
npm install
npx expo start
```

---

## 🛡️ Security & Privacy
- **Argon2id** password hashing (`time_cost=3`, `memory_cost=64MB`, `parallelism=4`).
- **RFC 7519 JWT** stateless access tokens with refresh token rotation.
- **DPDP Act 2023 Compliance**: Explicit user consent logging and immutable audit logs.
- **Cryptographic Provenance**: SHA-256 maker signature hashes embedded into physical QR codes.

---

## 📄 License
Developed for educational, cultural, and hackathon evaluation purposes under the Smart India Hackathon initiative.
