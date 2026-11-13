# CraftLens 2.0 – Known Limitations & Simulation Transparency

In accordance with our core engineering principles, CraftLens documents every simulated external transport, developmental constraint, and third-party prerequisite with complete honesty. No mock or fallback is hidden.

---

## 1. External Transport & Service Annotations (`STUB`)

| Service Component | File Location | Mode | Status & Behavior | Production Requirement |
|---|---|---|---|---|
| **SMS / OTP Delivery** | `backend/app/api/v1/endpoints/auth.py` | `STUB` | Emits OTP to backend logs and local debug responses. | Telecom DLT registration in India + Twilio/Gupshup/Karix API credentials. |
| **Bhashini / Whisper Multilingual ASR** | `backend/app/services/voice_catalog.py` | `HYBRID` | When `BHASHINI_API_KEY` or `OPENAI_API_KEY` is missing, falls back to deterministic rule-based NLP extraction with an honest `0.25` confidence score that forces artisan review. | National Language Translation Mission (NLTM) Bhashini enterprise credentials. |
| **Shiprocket Logistics Sandbox** | `backend/app/services/commerce_providers.py` | `SANDBOX` | Generates simulated test AWBs (`SR-EXP-*`) and deterministic shipment state progression. | Commercial Shiprocket merchant account with verified GSTIN and pickup warehouse address. |
| **Razorpay UPI Webhooks** | `backend/app/services/commerce_providers.py` | `TEST_MODE` | Uses Razorpay test key IDs (`rzp_test_*`) with HMAC-SHA256 signature verification. | Razorpay live account approval, business bank account, and public HTTPS webhook URL. |
| **ClamAV Anti-Malware Hook** | `backend/app/core/upload_security.py` | `OPTIONAL` | Validates file magic bytes (JPEG/PNG/WebP/WAV/MP3/M4A), strips EXIF, re-encodes images. ClamAV daemon scanned only if `CLAMAV_HOST` configured. | Running ClamAV network daemon (`clamd`) on TCP 3310. |
| **Sentry Error Tracking** | `backend/app/core/observability.py` & `mobile/src/services/telemetry.ts` | `OPTIONAL` | Initializes only if `SENTRY_DSN` is set; otherwise routes to structured JSON logger. Telemetry in mobile is strictly consent-gated by default. | Sentry.io project DSN or self-hosted GlitchTip instance. |

---

## 2. Local Environment & Hardware Constraints

### A. Local Docker Engine Unavailability
- **Condition**: On the current local development workstation (Windows 11 without active Docker Desktop daemon), containers cannot be started locally.
- **Verification Method**: All Dockerfiles (`backend/Dockerfile`, `buyer-web/Dockerfile`, `admin-web/Dockerfile`) are authored as multi-stage, pinned, non-root containers with `HEALTHCHECK` and are verified in GitHub Actions CI (`.github/workflows/ci.yml`).

### B. Headless Chrome / Lighthouse CLI
- **Condition**: Google Chrome / Lighthouse CLI is not installed on the host operating system path.
- **Verification Method**: Web performance is verified via Next.js 15 production static site generation, route chunk analysis (<102 kB first load JS), and CSS contrast audits documented in `docs/PERFORMANCE.md`.

### C. Deep Learning U2Net Model Weights
- **Condition**: Large deep-learning weights for U2Net (`~170 MB`) are not committed to git to keep clone times sub-second.
- **Behavior**: The AI Studio performs OpenCV-based adaptive edge thresholding, contrast enhancement, and studio white-fill. If `u2net.onnx` is placed in `ai-service/models/`, the service seamlessly switches to full deep-learning matting.

---

## 3. Security Boundary & Cryptographic Robustness

- **Ed25519 Provenance Keys**: In local development, an ephemeral Ed25519 keypair is auto-generated in `uploads/.heritage_ed25519_dev.pem`. In staging and production, `HERITAGE_ED25519_PRIVATE_KEY_PEM` must be injected as a 256-bit environment secret.
- **Secret Scanning**: Pre-commit hooks and GitHub Actions strictly prevent checking in live credentials (`rzp_live_*`, unencrypted private keys, or cloud provider tokens).

