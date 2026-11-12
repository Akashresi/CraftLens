# CraftLens 2.0 — Production Readiness Audit

**Audit Date:** 2026-11-12  
**Auditor Role:** Principal Full-Stack Engineer, Security Engineer & QA Lead  
**Method:** Static inspection of all repository directories + execution of read-only checks (`pytest`, `ruff`, `tsc`, `pnpm audit`, `pip check`, `pip list --outdated`). Zero code changes made during Phase 0.

---

## 1. Executive Summary

CraftLens 2.0 is a strong **hackathon prototype** with a well-structured SQLAlchemy 2.0 data model (39+ tables including `artisan_applications`), working Argon2id + JWT authentication, RBAC foundations, and unit tests that pass (`34 passed`). However, significant gaps prevent production pilot readiness:

- **`ai-service/` is empty** except `requirements.txt`; `docker-compose.yml` references `./ai-service/Dockerfile` which does not exist.
- **Voice ASR is a hardcoded stub** returning the same static Tamil string regardless of audio input (`backend/app/services/voice_catalog.py`).
- **Mobile Studio, Voice, Pricing, Orders, and Dashboard screens are client-side stubs** using `setTimeout` and hardcoded arrays (`mobile/app/(tabs)/*.tsx`).
- **Offline Sync is an in-memory `Map`**, despite claiming `expo-sqlite` persistence in comments (`mobile/src/services/offlineSync.ts`).
- **`buyer-web` fails TypeScript compilation** (6 errors due to importing non-existent `api` instead of `apiRequest` from `buyer-web/src/lib/api.ts`), causing pages to silently fall back to hardcoded demo arrays.
- **Security gaps**: plain SHA-256 QR hashes instead of Ed25519 signatures, missing rate limiting / account lockout, missing upload magic-byte verification / EXIF stripping, hardcoded dev `SECRET_KEY` and wildcard CORS `"*"` fallback, missing IDOR ownership checks on several artisan endpoints, and incomplete DPDP Act 2023 flows (no withdrawal/export/erasure/grievance).
- **Commerce gaps**: instant fake payment success on checkout with no Razorpay/UPI integration, webhooks, refunds, or order state machine; B2B missing GST invoicing.
- **Vulnerable frontend packages**: `buyer-web` `pnpm audit` reports **29 vulnerabilities** (3 critical, 11 high, 13 moderate, 2 low) primarily in `next@14.2.35` and `postcss@8.4.31`.

---

## 2. README & Architecture Claims vs. Reality

| Capability / Claim | Status | Exact File Paths | Detailed Findings |
|---|---|---|---|
| **Vision Pipeline** (bg removal, quality check, lighting, studio white, lifestyle) | **Partial** (Backend) / **Stub** (Mobile) | `backend/app/services/image_studio.py`, `backend/app/api/v1/endpoints/studio.py`, `mobile/app/(tabs)/studio.tsx`, `buyer-web/src/app/artisan/studio/page.tsx` | Backend has real OpenCV Laplacian blur + brightness/contrast check, GrabCut/optional `rembg` (disabled by default via `ENABLE_REMBG_DOWNLOAD=false`), CLAHE lighting, and PIL drop shadow + solid-color lifestyle compositing. **Gaps**: no cropping/framing feedback, no magic-byte/size/EXIF validation, synchronous blocking execution (no job queue). Mobile `studio.tsx` is a pure `setTimeout` stub with Unsplash URLs. |
| **Voice ASR / NLP** (Bhashini / Indic ASR + Gemini listing) | **Stub** (ASR) / **Partial** (NLP) | `backend/app/services/voice_catalog.py`, `backend/app/api/v1/endpoints/voice.py`, `mobile/app/(tabs)/voice.tsx` | `transcribe_regional_audio()` ignores `audio_bytes` and returns a hardcoded Tamil sentence with `confidence: 0.94`; Bhashini block is `if ...: pass`. `extract_and_generate_catalog()` uses deprecated `google.generativeai` when `GEMINI_API_KEY` is set, otherwise a 2-branch Tamil/Hindi keyword heuristic (`silk` / `clay` / generic). Mobile `voice.tsx` uses `setTimeout` mock data and imports non-existent `offlineSyncService`. |
| **Explainable Pricing Engine** | **Partial** | `backend/app/services/pricing_engine.py`, `backend/app/api/v1/endpoints/pricing.py`, `buyer-web/src/app/artisan/pricing/page.tsx`, `mobile/app/(tabs)/pricing.tsx` | Backend computes deterministic cost + fixed multipliers (`1.15`, `1.25`, `1.45` * rarity) and optional `MarketComparable` min/max lookup with an English text explanation. **Gaps**: no regional wage/tier adjustments, no override logging audit, `buyer-web` fails to import `api` so falls back to client math, mobile calculates purely locally and doesn't call backend. |
| **Cryptographic QR Provenance** | **Partial** (Weak Crypto) | `backend/app/services/heritage_service.py`, `backend/app/api/v1/endpoints/heritage.py`, `backend/app/models/heritage.py`, `buyer-web/src/app/heritage/[hash]/page.tsx` | Generates QR PNG via `qrcode` and stores `ProvenanceRecord` + `ProductQR`. **Gaps**: uses unsalted/static-salt SHA-256 (`CraftLens2026`), NOT Ed25519 digital signatures; no keypair management or revocation; `public_url` hardcoded to `http://localhost:3000`; `heritage.py` endpoints lack IDOR ownership checks; `buyer-web` page ignores backend failure and displays fake verified Vilachery provenance! |
| **Offline-First Sync (`expo-sqlite`)** | **Stub** | `mobile/src/services/offlineSync.ts`, `mobile/app/(tabs)/voice.tsx` | File header claims SQLite caching, retry queues & conflict resolution, but implementation only uses an in-memory `Map` (`loadDraftsFromStorage()` is an empty comment). No `expo-sqlite` persistence, no conflict resolution policy, no idempotency keys, no exponential backoff, hardcoded `127.0.0.1:8000`. |
| **DPDP Act 2023 Compliance & Audit Logging** | **Partial** | `backend/app/api/v1/endpoints/compliance.py`, `backend/app/models/user.py` (`ConsentRecord`, `AuditLog`) | Records consent grant/flag (`POST /consent`) and lists consents (`GET /consent`) with IP and audit entry. **Gaps**: no consent withdrawal workflow enforcement, no user data export endpoint, no data erasure/anonymization endpoint, no grievance officer contact endpoint/UI, no DB/application append-only protection on `AuditLog`. |
| **B2B Bulk Orders & Wholesale** | **Partial** (Backend) / **Stub** (Web/Mobile) | `backend/app/api/v1/endpoints/b2b.py`, `backend/app/models/b2b.py`, `buyer-web/src/app/b2b/page.tsx`, `mobile/app/(tabs)/orders.tsx` | Backend supports RFQ -> Quotation -> PO creation with milestones. **Gaps**: missing GST/HSN invoicing fields, missing IDOR check on `accept_quotation_and_generate_po`, `buyer-web/src/app/b2b/page.tsx` imports broken `api` and displays `DEMO_QUOTATIONS`, mobile B2B tab uses static mock array. |
| **Retail Checkout, Payments & Shipping** | **Stub** (Payments/Shipping) / **Partial** (Orders) | `backend/app/api/v1/endpoints/orders.py`, `backend/app/models/order.py`, `buyer-web/src/app/cart/page.tsx` | Backend `POST /orders/checkout` deducts inventory atomically, creates `Order`, immediately hardcodes `Payment(status="SUCCESS")` and `Shipment(status="MANIFESTED")`. No Razorpay order creation, UPI verification, webhook signature verification, refunds, or order state transitions. `buyer-web/src/app/cart/page.tsx` never even calls the backend! |
| **Admin Moderation & Governance** | **Partial** | `admin-web/src/app/page.tsx`, `backend/app/api/v1/endpoints/artisan_applications.py` | Artisan application review (`GET /admin`, `/approve`, `/reject`) is genuinely connected to FastAPI. **Gaps**: `admin-web` hardcodes `admin@craftlens.org` / `CraftLensAdmin@2026` auto-login in client JS! Catalog Moderation, AI Pipeline Health, and DPDP Consent Logs tabs in `admin-web` are 100% static demo arrays. No GI-claim verification endpoint. |
| **Authentication & RBAC** | **Partial** | `backend/app/core/security.py`, `backend/app/core/config.py`, `backend/app/api/deps.py`, `backend/app/api/v1/endpoints/auth.py`, `mobile/app/(buyer-tabs)/*`, `mobile/app/(tabs)/_layout.tsx` | Argon2id password hashing + JWT access/refresh tokens + 4 roles + buyer-to-artisan application workflow implemented and tested. **Gaps**: no rate limiting or account lockout on `/auth/login`, dev `SECRET_KEY` in `config.py`, `"*"` in `CORS_ORIGINS`, no refresh token revocation/rotation store, several artisan/buyer endpoints lack IDOR ownership checks. |
| **Standalone AI Service & Queue (`ai-service/`)** | **Missing** | `ai-service/requirements.txt`, `docker-compose.yml` | Only `ai-service/requirements.txt` exists. `ai-service/Dockerfile`, FastAPI service code, Celery/RQ worker, and `/ai-service/evals` do not exist. `docker-compose.yml` cannot build `ai-service`. |
| **Docker & CI Pipeline** | **Broken / Partial** | `docker-compose.yml`, `backend/Dockerfile`, `.github/workflows/ci.yml` | `docker-compose.yml` references missing `./ai-service/Dockerfile`, omits `buyer-web`/`admin-web`, embeds default DB credentials. `backend/Dockerfile` runs as `root` with `--reload` and unpinned deps. `.github/workflows/ci.yml` only runs `pytest` (missing lint, typecheck, coverage threshold, `buyer-web`/`admin-web`/`mobile` checks, security scans, Docker build). |

---

## 3. Repository-Wide Tooling & Test Baseline (Observed)

| Check | Command Run | Result |
|---|---|---|
| Backend tests | `python -m pytest backend/tests -q` | **34 passed**, 1 `FutureWarning` (`google.generativeai` deprecated) in 16.06s. Note: tests directly invoke endpoint functions with DB session rather than HTTP `TestClient`, bypassing FastAPI auth/rate-limit middleware on some paths. |
| Python dependency integrity | `python -m pip check` | `No broken requirements found.` |
| Ruff linter | `python -m ruff check backend --statistics` | **650 errors** (`147 F401`, `121 UP045`, `109 B008`, `72 I001`, `68 UP017`, `37 UP035`, `34 UP006`, `31 F821` undefined names in `app/models` / tests, `8 UP007`, `8 F841`, `5 BLE001`, `3 FURB188`, `2 S110`, `2 C401`, `2 RUF022`, `1 UP012`). |
| `buyer-web` TypeScript | `cd buyer-web; npx tsc --noEmit` | **Failed (exit 1)** — 6 errors in `artisan/dashboard/page.tsx`, `artisan/pricing/page.tsx`, `b2b/page.tsx`, `catalog/page.tsx`, `heritage/[hash]/page.tsx`. |
| `admin-web` TypeScript / deps | Checked `admin-web/node_modules` | `node_modules` not installed locally; not typechecked yet. |
| `mobile` TypeScript / deps | Checked `mobile/node_modules` | `node_modules` not installed locally; `voice.tsx` has broken import `offlineSyncService` vs `offlineSyncEngine`. |
| Docker availability | `docker --version` | **`docker` not installed** on this Windows host. Docker builds/compose cannot be executed locally unless Docker is installed (CI will validate). |
| Missing QA/security Python tools | `python -m pip show bandit mypy pip-audit pytest-cov` | **Not installed** (`bandit`, `mypy`, `pip-audit`, `pytest-cov` missing). |

---

## 4. Dependency, Outdated Package & Vulnerability Inventory

### 4.1 Python Dependencies (`backend/requirements.txt` & `ai-service/requirements.txt`)
- **All requirements use unpinned `>=` ranges** (non-reproducible builds).
- **`google-generativeai` (`0.8.6`)** emits deprecation warning (`FutureWarning: All support for the google.generativeai package has ended... Please switch to google.genai`).
- **`pip list --outdated`** reported **101 outdated packages** in the host Python environment, including core framework & crypto deps:
  - `cryptography`: `46.0.3` -> `50.0.2`
  - `fastapi`: `0.121.2` -> `0.162.5`
  - `starlette`: `0.49.3` -> `1.10.0`
  - `PyJWT`: `2.11.0` -> `2.15.1`
  - `python-multipart`: `0.0.22` -> `0.0.33`
  - `urllib3`: `2.5.0` -> `2.8.0`
  - `requests`: `2.32.5` -> `2.34.2`
  - `Werkzeug`: `3.1.3` -> `3.1.9`
  - `pypdf`: `6.21.4` -> `7.0.1`
  - `pillow`: `13.0.0` (current), `bcrypt`: `3.2.0` -> `5.0.0`, `ecdsa`: `0.19.1` -> `0.19.2`, `protobuf`: `5.29.6` -> `7.36.2`, `torch`: `2.10.0` -> `2.15.0`.
- **`pip-audit`**: not installed yet (will install in Phase 1 and run full CVE scan).

### 4.2 Node / Frontend Dependencies (`buyer-web`, `admin-web`, `mobile`)
- **`buyer-web` (`pnpm audit --json`)**: **29 vulnerabilities** across 108 dependencies (`3 critical`, `11 high`, `13 moderate`, `2 low`):
  - **Critical (3)** in `next@14.2.35`:
    - `GHSA-p293-qw3h-jr36`: Unauthenticated RCE on Windows-hosted servers (`next <15.5.24`)
    - `GHSA-2xp9-vwfh-vxw4`: Unauthenticated RCE in Image Optimization API with AVIF (`next <15.5.24`)
    - `GHSA-2464-fhr4-w9xw`: Unauthenticated RCE in Image Optimization API with SVG (`next <=15.5.27`)
  - **High / Moderate** in `next@14.2.35` (Server Actions DoS `GHSA-p3m5-59mp-jv5r`, `GHSA-q4gf-8mx6-v5v3`, `GHSA-8h8q-6873-q5fj`, SSRF/deserialization `GHSA-h25m-26qc-wcjf`) and `postcss@8.4.31` (arbitrary `.map` file disclosure `GHSA-6g55-p6wh-862q`, `GHSA-r28c-9q8g-f849`, XSS `GHSA-qx2v-qp2m-jg93`).
- **`admin-web`**: Uses same vulnerable `next@^14.2.15`, lacks lockfile & `node_modules`.
- **`mobile`**: Uses Expo `~51.0.0`, React Native `0.74.5`, lacks lockfile & `node_modules`.

---

## 5. Immediate Risks Prioritized for Subsequent Phases

1. **Broken Web & Mobile Compilation/Runtime** (Phase 1 & 5/6): `buyer-web` imports missing `api`; `mobile` `voice.tsx` imports missing `offlineSyncService`; `ai-service` is missing `Dockerfile` and code.
2. **Critical CVEs in Next.js 14** (Phase 1/2): `next@14.2.35` has 3 critical RCE advisories; requires upgrade to patched Next.js 15.x or latest patched LTS.
3. **Hardcoded Secrets & Weak Provenance** (Phase 2): Dev `SECRET_KEY` in code, client-side hardcoded admin password in `admin-web`, SHA-256 QR without Ed25519 signature, missing IDOR checks, missing rate limiting, and unvalidated file uploads.
4. **Silent Stubs Misrepresented as Working** (Phase 3/4/5): Simulated mobile studio/voice/orders, hardcoded ASR return string, in-memory offline sync, fake checkout payment/shipment creation.

