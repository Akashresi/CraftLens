# CraftLens 2.0 — Production Hardening Progress Tracker

Methodology: **ACT -> VERIFY -> RECORD** (evidence required for every ticked item).

---

## PHASE 0: AUDIT (No Code Changes)
- [x] Read every folder (`backend/app/services`, `backend/app/api`, `backend/app/models`, `ai-service`, `mobile`, `buyer-web`, `admin-web`, `docker-compose.yml`, `.github/workflows/ci.yml`).
  - Evidence: Inspected files directly; findings recorded in `docs/AUDIT.md`.
- [x] Produce `/docs/AUDIT.md` mapping README claims to `Implemented / Partial / Stub / Missing` with file paths.
  - Evidence: Created `docs/AUDIT.md`.
- [x] List dependencies, outdated packages, and known vulnerabilities.
  - Evidence: `python -m pip check` -> `No broken requirements found.`; `python -m pip list --outdated --format=json` -> 101 outdated packages; `cd buyer-web; pnpm audit --json` -> 29 vulnerabilities (3 critical, 11 high, 13 moderate, 2 low); `python -m ruff check backend --statistics` -> 650 errors; `cd buyer-web; npx tsc --noEmit` -> 6 TypeScript errors.
- [x] **PHASE 0 GATE PASSED**: `docs/AUDIT.md` complete and accurate.

---

## PHASE 1: FOUNDATION AND QUALITY
- [ ] Run full test suite & install QA/security tooling (`ruff`, `mypy`, `pytest-cov`, `pip-audit`, `bandit`, `pre-commit`).
- [ ] Fix failing/broken TypeScript builds (`buyer-web`, `admin-web`, `mobile`), ESLint/Prettier/tsc strict configs.
- [ ] Fix Python lint/type issues (`ruff`, `mypy`) and add `pyproject.toml` / `.pre-commit-config.yaml`.
- [ ] Achieve >= 80% backend test coverage across every endpoint including failure cases.
- [ ] Complete `ai-service` skeleton/Docker/compose parity so `docker compose` builds cleanly from `.env.example`.
- [ ] Upgrade CI (`.github/workflows/ci.yml`) for lint, typecheck, coverage >= 80%, dependency audit, and Docker build.
- [ ] **PHASE 1 GATE**

---

## PHASE 2: SECURITY HARDENING
- [ ] Rate limiting (login, OTP/register, uploads, voice), account lockout, strict CORS allowlists, security headers.
- [ ] Upload validation: magic bytes, size limits, image re-encoding, malware-scan hook, EXIF stripping.
- [ ] Move secrets to environment variables, secret scanning in CI (`gitleaks`/pattern check), document/rotate any repo secrets.
- [ ] Enforce RBAC + IDOR ownership checks on all endpoints with negative/IDOR tests.
- [ ] Prevent SQLi/XSS and add CSRF protection where cookies are used.
- [ ] Provenance: Ed25519 signed payloads, public key store, verification endpoint, public verification page (no fake fallback), revocation.
- [ ] Complete DPDP Act 2023 flows: consent capture/withdrawal, data export, data erasure, grievance contact, append-only audit log protection.
- [ ] Write threat model in `/docs/SECURITY.md` + verify `bandit`/`semgrep`/`npm audit` clean.
- [ ] **PHASE 2 GATE**

---

## PHASE 3: AI QUALITY (REAL, MEASURED)
- [ ] Vision: real background cleanup & enhancement + blur, lighting, and cropping feedback.
- [ ] Voice: multilingual ASR adapter for Indian languages (`ta`, `hi`, `te`, `kn`, `ml`, `bn`, `mr`) + low-confidence fallback.
- [ ] Listing generation in artisan's language with mandatory review-and-confirm step (never auto-publish).
- [ ] Pricing: materials, labour hours, region & comparables + "why this price" breakdown + artisan override logging.
- [ ] Build `/ai-service/evals` dataset & script; publish honest metrics in `/docs/AI_EVAL.md`.
- [ ] Async AI job queue (Celery/RQ with Redis) with status polling, retries, and timeouts.
- [ ] **PHASE 3 GATE**

---

## PHASE 4: COMMERCE COMPLETENESS
- [ ] Razorpay (test mode) + UPI payment flow, idempotent webhooks with signature verification, refunds.
- [ ] Full order state machine (`placed`, `paid`, `packed`, `shipped`, `delivered`, `cancelled`, `returned`, `disputed`) + transition tests.
- [ ] Shipping provider interface + sandbox adapter.
- [ ] Seller KYC hook, GI-claim verification workflow in `admin-web`, reviews, and dispute handling.
- [ ] B2B bulk RFQs, quotes, and GST invoicing.
- [ ] Localized Notification provider interface (SMS/WhatsApp/email).
- [ ] End-to-end sandbox commerce test (listing -> payment -> shipped -> delivered -> payout).
- [ ] **PHASE 4 GATE**

---

## PHASE 5: MOBILE AND OFFLINE-FIRST
- [ ] Offline draft sync using `expo-sqlite` / persistent adapter, conflict policy (`last-write-wins` + conflict log), idempotent endpoints, exponential backoff.
- [ ] Low-literacy UX: large touch targets (>= 48dp), icon-first screens, voice prompts, minimal text input.
- [ ] Accessibility: screen reader labels, >= 4.5:1 contrast, low-end optimization notes.
- [ ] Privacy-respecting consent-based analytics & crash reporting hook.
- [ ] Scripted offline create-listing -> reconnect -> sync test with zero data loss.
- [ ] **PHASE 5 GATE**

---

## PHASE 6: WEB, PERFORMANCE AND UX
- [ ] `buyer-web`: SEO metadata, Schema.org Product JSON-LD, image optimization, loading/error/empty states, full language switching.
- [ ] `admin-web`: live moderation queue, seller KYC verification, GI verification, analytics dashboard, audit log viewer.
- [ ] Lighthouse checks / targets (Perf >= 85, A11y >= 95, SEO >= 90) or documented shortfall/plan.
- [ ] Backend DB indexes, pagination everywhere, N+1 prevention, Redis caching for catalog reads.
- [ ] Load test (Locust / k6) at 100 and 500 concurrent users -> `/docs/PERFORMANCE.md`.
- [ ] **PHASE 6 GATE**

---

## PHASE 7: OPERATIONS
- [ ] Structured JSON logging with request IDs, Sentry integration, `/health` & `/ready` endpoints, Prometheus `/metrics` + dashboard config.
- [ ] Automated DB backup script + tested restore procedure.
- [ ] Forward & backward Alembic migrations tested cleanly on fresh DB.
- [ ] Multi-stage non-root pinned Dockerfiles, staging deploy workflow, zero-downtime notes.
- [ ] `/docs/RUNBOOK.md`.
- [ ] **PHASE 7 GATE**

---

## PHASE 8: DOCUMENTATION AND DEMO
- [ ] Honest `README.md` rewrite with architecture diagram, `LICENSE`, `CONTRIBUTING.md`, repo topics/description.
- [ ] Realistic seed data + 5-minute demo script.
- [ ] `/docs/KNOWN_LIMITATIONS.md` & `/docs/PILOT_PLAN.md` (1 craft cluster, 20-50 artisans, NGO verification partner, success metrics).
- [ ] **PHASE 8 GATE**
