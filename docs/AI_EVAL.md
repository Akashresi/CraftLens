# CraftLens Phase 3 — AI Quality & Evaluation Report

**Evaluation Command:** `python ai-service/evals/run_evals.py`  
**Dataset:** `ai-service/evals/dataset.json` (16 multilingual transcripts across 8 languages, 6 craft categories; 6 regional pricing cases; 5 controlled synthetic vision images)

---

## 1. Vision Studio Quality & Cropping Detection

| Metric | Measured Result | Notes |
| --- | --- | --- |
| Test Cases | 5 / 5 passed (`100%` accuracy) | `balanced_crisp`, `blurry_photo`, `too_dark_photo`, `edge_cropped`, `subject_too_small` |
| Average Quality Latency | `2.46 ms` per image | OpenCV Laplacian blur + Canny edge bounding-box framing analysis |
| Cropping Detection | Working | Flags subjects touching edges (`coverage > 75%`) and small subjects (`coverage < 12%`) |

**Known Limitation:** Background removal uses lightweight OpenCV GrabCut/morphological mask cleanup unless `ENABLE_REMBG_DOWNLOAD=true` is enabled to fetch U2Net weights (`rembg`), so fine hair-like bamboo fibers on cluttered backgrounds perform better when U2Net is enabled.

---

## 2. Multilingual Indian ASR (8 Languages)

Supported languages in `backend/app/services/voice_catalog.py`: `ta` (Tamil), `hi` (Hindi), `te` (Telugu), `kn` (Kannada), `ml` (Malayalam), `bn` (Bengali), `mr` (Marathi), and `en` (English).

| Language | Active Provider (Clean Env) | Confidence Returned | Fallback Triggered | Live Speech WER |
| --- | --- | --- | --- | --- |
| Tamil (`ta`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |
| Hindi (`hi`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |
| Telugu (`te`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |
| Kannada (`kn`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |
| Malayalam (`ml`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |
| Bengali (`bn`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |
| Marathi (`mr`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |
| English (`en`) | `offline_low_confidence_fallback` | `0.25` | `true` | `null` (no `BHASHINI_API_KEY` configured) |

**Honesty & Limitations:**
- Previous prototype behavior returned a hardcoded fake `0.94` confidence and canned Tamil transcript. That silent mock has been removed.
- Without `BHASHINI_API_KEY` / `BHASHINI_USER_ID` / `BHASHINI_PIPELINE_ID` (or `ENABLE_WHISPER_ASR=true` with model weights downloaded), audio transcription returns `confidence = 0.25`, `fallback_used = true`, and `needs_confirmation = true` so artisans verify or enter text manually.
- Regional-language Word Error Rate (`WER`) on real noisy studio recordings remains unmeasured until Bhashini ULCA credentials and field audio recordings are supplied during pilot onboarding.

---

## 3. Multilingual Listing Extraction & Confirmation Safety

Evaluated across `16` benchmark transcripts (`2` per language across all 8 supported languages) covering all `6` seeded craft categories:

| Metric | Measured Result |
| --- | --- |
| Category Prediction Accuracy | `100.0%` (`16 / 16`) |
| Primary Material Match Accuracy | `100.0%` (`16 / 16`) |
| Artisan Confirmation Guard (`DRAFT_PREVIEW` + `requires_artisan_confirmation=True`) | `100.0%` (`16 / 16`) |

`POST /api/v1/voice/apply-to-product` rejects requests where `artisan_confirmed` is `false` (`HTTP 400`), preventing unreviewed AI drafts from mutating live catalog products.

**Known Limitation:** Deterministic fallback uses keyword extraction across the 6 craft categories; free-form nuanced craft stories outside those keyword vocabularies require `GEMINI_API_KEY` for rich narrative generation, and non-Hindi local titles prefix the localized label onto the English title template in offline mode.

---

## 4. Explainable Craft Pricing Engine

Evaluated across `6` craft benchmarks spanning Tamil Nadu, Karnataka, West Bengal, Maharashtra, Chhattisgarh, and Kerala (`ai-service/evals/dataset.json`):

| Metric | Measured Result |
| --- | --- |
| Mean Absolute Error (MAE vs fair-wage cost-plus baseline) | `₹1.06` |
| Mean Absolute Percentage Error (MAPE) | `0.03%` |
| Regional Living-Wage Floor Enforcement Rate | `100.0%` (`6 / 6`) |

Every quote returns a structured `why_this_price` dictionary detailing `materials_inr`, `labor_inr`, `labor_hours`, `effective_hourly_wage_inr`, `packaging_and_shipping_inr`, `overhead_inr`, `region_state`, `regional_index`, `heritage_rarity_multiplier`, `comparables_matched`, and `retail_margin_percent`. Artisan price overrides are logged into both `PricingHistory` and append-only `AuditLog`.

**Known Limitation:** Reference targets in `dataset.json` test alignment against the regional living-wage formula rather than external scraped marketplace prices. Market comparable blending activates only when matching `MarketComparable` records exist in PostgreSQL/SQLite.

---

## 5. Async Job Queue (`backend/app/services/job_queue.py`)

Heavy studio processing exposes `POST /api/v1/studio/process-async` and `GET /api/v1/studio/jobs/{job_id}` (owner or `ADMIN` only), persisting job state in `ai_jobs` (`QUEUED -> PROCESSING -> COMPLETED | FAILED`), pushing descriptors to Redis (`craftlens:ai_jobs`) when configured, enforcing `30s` timeouts and up to `2` retries with local `ThreadPoolExecutor` fallback when Redis is absent.

