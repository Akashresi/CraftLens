# Contributing to CraftLens 2.0

Thank you for your interest in contributing to **CraftLens**, an open-source, AI-powered artisan commerce and provenance platform designed to empower traditional craftspeople with ethical AI tooling, fair pricing, and cryptographic provenance.

---

## 1. Monorepo Overview

| Directory | Stack / Role | Key Commands |
|---|---|---|
| `backend/` | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 | `python -m pytest backend/tests --cov=backend/app` |
| `buyer-web/` | Next.js 15, React 18, Tailwind CSS, Lucide | `pnpm dev`, `pnpm build`, `pnpm lint` |
| `admin-web/` | Next.js 15, React 18, Tailwind CSS | `pnpm dev`, `pnpm build`, `pnpm lint` |
| `mobile/` | React Native (Expo SDK 52), TypeScript | `npx expo start`, `npx tsc --noEmit` |
| `ai-service/` | Vision framing, multilingual ASR, living wage pricing | `python -m ruff check ai-service` |
| `scripts/` | Backup drills, load testing, demo seeding | `python scripts/seed_demo.py` |
| `docs/` | Architecture, Security, AI Evals, Runbooks | Markdown documentation |

---

## 2. Local Development Setup

### Prerequisites
- **Python**: 3.11+ (Python 3.11 or 3.13)
- **Node.js**: 20.x LTS
- **Package Manager**: `pnpm` (v10+ or v12+)
- **Git**

### Installation
```bash
# 1. Clone repository
git clone https://github.com/craftlens/craftlens.git
cd craftlens

# 2. Configure environment variables
cp .env.example .env

# 3. Setup Backend
python -m pip install -r backend/requirements-dev.txt
cd backend
python -m alembic upgrade head
cd ..

# 4. Setup Web & Mobile
pnpm --filter buyer-web install
pnpm --filter admin-web install
cd mobile && pnpm install && cd ..
```

---

## 3. Development Workflow & Quality Gates

CraftLens enforces an **ACT -> VERIFY -> RECORD** methodology. Every change must be verified against real local command output before opening a pull request.

### Quality Checklist Before PR

```bash
# 1. Backend Linting & Formatting Check
python -m ruff check backend ai-service scripts
python -m ruff format --check backend ai-service scripts

# 2. Static Type Checking
python -m mypy backend/app ai-service

# 3. Security Static Analysis
python -m bandit -r backend/app ai-service -ll -q

# 4. Dependency Vulnerability Audit
python -m pip_audit -r backend/requirements.txt --no-deps

# 5. Full Backend Pytest Suite with >= 80% Coverage
python -m pytest backend/tests --cov=backend/app --cov-report=term-missing --cov-fail-under=80 -v

# 6. Database Migration Idempotency & Reversibility
python -m pytest backend/tests/test_migrations_reversible.py -v

# 7. Web Application Typecheck, Lint & Build
cd buyer-web && pnpm typecheck && pnpm lint && pnpm build && cd ..
cd admin-web && pnpm typecheck && pnpm lint && pnpm build && cd ..

# 8. Mobile Typecheck
cd mobile && npx tsc --noEmit && cd ..
```

---

## 4. Git Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(<scope>)`: A new feature (e.g., `feat(voice): add Kannada and Telugu ASR support`)
- `fix(<scope>)`: A bug fix (e.g., `fix(order): prevent duplicate inventory deduction on payment retry`)
- `docs(<scope>)`: Documentation changes only (e.g., `docs(runbook): add secret rotation steps`)
- `test(<scope>)`: Adding missing tests or correcting existing tests
- `refactor(<scope>)`: Code change that neither fixes a bug nor adds a feature
- `perf(<scope>)`: Code change that improves performance

---

## 5. Security & DPDP Act 2023 Guidelines

- **Never Commit Secrets**: Never commit private keys, real payment gateway credentials, or API tokens. Secrets must only be loaded from environment variables.
- **Role-Based Access Control**: Never trust user roles supplied by client applications; enforce RBAC (`ADMIN`, `ARTISAN`, `RETAIL_BUYER`, `WHOLESALE_BUYER`) on every backend API endpoint.
- **DPDP Act 2023**: Any collection of user data requires explicit consent logging via `/api/v1/compliance/consent`. Respect data export and erasure requests.
- **Label Stubs Honestly**: Any simulated external transport (e.g., SMS OTP, Shiprocket sandbox carrier, live third-party ASR) must be explicitly annotated as `"STUB"` in the code and logged in `docs/KNOWN_LIMITATIONS.md`.

