# CraftLens 2.0 — Security Architecture & Threat Model

**Document Version:** 2.0  
**Last Updated:** 2026-11-12  
**Scope:** FastAPI Backend, `ai-service`, `buyer-web`, `admin-web`, Expo Mobile App, PostgreSQL, Redis.

---

## 1. System Trust Boundaries

```
[Untrusted Clients: Mobile / Browser / Public QR Scanners]
        │  TLS (prod), Strict CORS Allowlist, Rate Limit, Security Headers
        ▼
[FastAPI Edge & Auth Layer]
   ├── Argon2id (t=3, m=64MB, p=4) + Account Lockout (5 fails -> 15m lock)
   ├── RFC 7519 HS256 JWT (60m access / 30d refresh) + Double-Submit CSRF (cookies)
   └── RBAC (`require_role`) + Resource Ownership Checks (IDOR Prevention)
        │
        ├──► [Upload Gatekeeper] (Magic Bytes, Size <=10/15MB, EICAR/ClamAV, PIL EXIF Strip)
        ├──► [Ed25519 Provenance Signer] (Asymmetric signing + Key Export + Revocation)
        └──► [DPDP Act 2023 Compliance Engine] (Consent/Withdraw, Export, Erase, Append-Only AuditLog)
```

---

## 2. STRIDE Threat Model & Mitigations

| Category | Threat | Control Implemented | File / Mechanism |
|---|---|---|---|
| **Spoofing** | Brute-force credential stuffing against artisan/admin logins | Sliding-window IP rate limit + DB account lockout (`423 Locked` after 5 failed passwords for 15 min) | `backend/app/core/rate_limit.py`, `backend/app/api/v1/endpoints/auth.py` |
| **Spoofing** | Client-supplied `role_code="ARTISAN"` or `"ADMIN"` privilege escalation | Public `/auth/register` rejects `ARTISAN`/`ADMIN` (`400`); conversion requires admin review transaction | `backend/app/api/v1/endpoints/auth.py`, `artisan_applications.py` |
| **Tampering** | Forged QR heritage provenance tags or stale revoked products | Canonical JSON signed by **Ed25519** private key; public `/heritage/verify/{qr_hash}` validates signature & `is_revoked` | `backend/app/services/heritage_service.py`, `endpoints/heritage.py` |
| **Tampering** | Altering or deleting security audit history | SQLAlchemy `before_update` / `before_delete` ORM guards raise `ValueError` | `backend/app/models/user.py` (`AuditLog`) |
| **Tampering / Code Exec** | Malicious polyglot image/script uploads or path traversal filenames | Magic-byte inspection (JPEG/PNG/WEBP, WAV/MP3/OGG/FLAC/M4A/WEBM), size cap, EICAR/ClamAV malware hook, Pillow decode + re-encode (strips EXIF & embeds), fixed UUID filenames | `backend/app/core/upload_security.py`, `endpoints/studio.py`, `voice.py` |
| **Repudiation** | Denying admin approval, lockout, or DPDP consent actions | Append-only `AuditLog` capturing `user_id`, `action`, `resource`, `ip_address`, `details`, `created_at` | `backend/app/models/user.py`, `compliance.py`, `artisan_applications.py` |
| **Information Disclosure** | IDOR cross-user access (artisan pricing another's item, buyer reading another's order) | Explicit ownership assertions (`_assert_product_owner_or_admin`, buyer/artisan checks in `orders.py`, `b2b.py`, `pricing.py`) tested with negative cases | `pricing.py`, `heritage.py`, `b2b.py`, `orders.py` |
| **Information Disclosure** | Hardcoded secrets in client JS (`admin-web`) or `config.py` / `docker-compose.yml` | Removed hardcoded `admin-web` credentials (replaced with real sign-in UI); `SECRET_KEY` auto-generated ephemerally in dev and strictly validated in prod; compose parameterized via `.env` | `backend/app/core/config.py`, `admin-web/src/app/page.tsx`, `docker-compose.yml` |
| **DoS / Abuse** | High-cost image/voice pipeline flooding | Per-IP sliding-window rate limits (`20-25 req/min`) + upload max sizes (`10MB` image / `15MB` audio) | `backend/app/core/rate_limit.py` |
| **Elevation / Injection** | SQL injection, Stored XSS, CSRF on cookie sessions, clickjacking | SQLAlchemy parameterized ORM queries; `sanitize_text` HTML/script stripping; double-submit `X-CSRF-Token` middleware; OWASP response headers (`X-Frame-Options: DENY`, `nosniff`, `CSP`) | `backend/app/main.py`, `backend/app/core/upload_security.py` |

---

## 3. Secret Management & Rotation Policy

- **Previously Committed Dev Artifacts**: Earlier hackathon commits contained placeholder dev secrets in `backend/app/core/config.py`, `docker-compose.yml`, and `admin-web/src/app/page.tsx`. All hardcoded credentials in `admin-web` and static fallback `SECRET_KEY` in `config.py` have been removed.
- **Production Rotation Checklist**:
  1. Generate a fresh 64-byte `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(48))"`
  2. Generate an independent Ed25519 provenance signing keypair and set `HERITAGE_ED25519_PRIVATE_KEY_PEM` in secret manager.
  3. Rotate `POSTGRES_PASSWORD`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, `GEMINI_API_KEY`, and `BHASHINI_API_KEY` before deploying to staging/production.
  4. Never reuse the demonstration seeded password (`CraftLensAdmin@2026` / `Artisan@2026`) outside local development; reset immediately after initial bootstrap.
  5. CI executes `git grep` secret scanning on every PR to block private keys or live API tokens.

---

## 4. DPDP Act 2023 Compliance Controls

- **Notice & Consent**: Explicit consent capture (`POST /api/v1/compliance/consent`) and withdrawal (`POST /api/v1/compliance/consent/{type}/withdraw`).
- **Right to Access**: Full JSON personal data export (`GET /api/v1/compliance/export-my-data`).
- **Right to Erasure**: PII anonymization + account deactivation (`POST /api/v1/compliance/erase-my-data`) preserving statutory financial/audit history without PII.
- **Grievance Redressal**: Dedicated Grievance Officer contact (`GET /api/v1/compliance/grievance-contact`) and user grievance ticket tracking (`POST`/`GET /api/v1/compliance/grievance`).
- **Immutable Audit Trail**: Append-only `AuditLog` model protected by ORM update/delete guards.

---

## 5. Known Residual Security Considerations

- **Rate Limiter Storage**: Default `SlidingWindowRateLimiter` uses process-local memory; multi-worker production deployments must configure shared Redis storage (wired in Operations/Phase 6–7).
- **Antivirus Daemon**: Malware hook checks EICAR test signatures inline and streams to `clamd` when `CLAMAV_HOST` is set; if `CLAMAV_HOST` is empty (dev/CI), external virus scanning is skipped and documented.
- **Next.js Transitive `postcss`**: `buyer-web` and `admin-web` use `next@15.5.29` (0 critical CVEs); Next's internal `postcss` package triggers 2 moderate / 2 high advisory notices during build-time CSS processing only.
