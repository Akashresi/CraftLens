# CraftLens 2.0 – 5-Minute Pilot & Judge Demonstration Walkthrough

This demo script provides a step-by-step walkthrough to present the end-to-end CraftLens platform in 5 minutes, covering both the artisan empowerment experience and buyer provenance verification.

---

## Pre-Flight Setup & Demo Credentials

Ensure the platform is seeded and services are running:
```bash
# Seed realistic demonstration catalog, artisans, GI tags, and orders
python scripts/seed_demo.py

# Start services (or docker compose up)
# Terminal 1: Backend
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
# Terminal 2: Buyer Web
pnpm --filter buyer-web dev
# Terminal 3: Admin Web
pnpm --filter admin-web dev
```

### Pre-Seeded Demonstration Accounts

| Role | Email | Password | Persona / Context |
|---|---|---|---|
| **Master Artisan** | `artisan@craftlens.org` | `Artisan@2026` | Meenakshi Ammal, Kanchipuram Silk Weaver (Tamil) |
| **Master Artisan** | `artisan.nagaraj@craftlens.org` | `Artisan@2026` | Nagaraj Gowda, Channapatna Toymaker (Kannada) |
| **Retail Buyer** | `buyer@craftlens.org` | `Buyer@2026` | Ananya Sharma, Bengaluru (Retail Shopper) |
| **B2B Wholesale** | `wholesale@craftlens.org` | `Wholesale@2026` | Vikram Birla, Craft Traditions Exports (GST: 27AAACR1234F1Z5) |
| **Platform Admin** | `admin@craftlens.org` | `CraftLensAdmin@2026` | Chief Governance & Verification Officer |

---

## 5-Minute Demonstration Timeline

```mermaid
timeline
    title CraftLens 5-Minute Pilot Walkthrough
    0:00 - 0:45 : Context & Problem : Artisan challenges, middlemen exploitation, fake handicraft infiltration
    0:45 - 1:45 : Mobile AI Studio : Live framing analysis, blur & contrast checks, studio background enhancement
    1:45 - 2:45 : Multilingual Voice : Dialect voice input, NLP entity extraction, artisan confirmation gate
    2:45 - 3:30 : Fair Pricing : Living wage calculation, transparent cost breakdown, artisan overrides
    3:30 - 4:15 : Buyer Provenance : Ed25519 QR signature verify, GI origin cluster, UPI checkout
    4:15 - 5:00 : Admin Governance : KYC & GI verification, DPDP audit trail, Prometheus metrics
```

---

### Step 1 (0:00 – 0:45): The Challenge & Vision
- **Narration**: *"Over 7 million traditional artisans in India lack digital literacy and e-commerce access. Middlemen take up to 70% of the margins, while machine-made counterfeits undermine Geographical Indication (GI) heritage. CraftLens provides an AI-first, voice-native platform that puts power and fair compensation back into artisans' hands."*
- **Visual**: Show Mobile App (`http://localhost:8081` or Expo simulator) showcasing large 48dp+ icon-first buttons and local language switcher.

---

### Step 2 (0:45 – 1:45): Mobile AI Studio & Framing Quality Feedback
- **Action**: Open Mobile AI Studio tab (`/studio`).
- **Feature Demonstrated**:
  - Artisan snaps or uploads a craft photo on a cluttered workshop table.
  - **Live Quality Check**: OpenCV-backed computer vision evaluates sharpness (Laplacian variance), illumination, and object centering.
  - **Artisan Guidance**: The app displays actionable, friendly feedback (e.g., *"Photo is sharp! Move closer to center the craft"*).
  - **Background Cleanup**: AI isolates the foreground craft, replacing the cluttered workshop backdrop with an e-commerce-ready pure white studio or aesthetic lifestyle background.
- **Reference**: See [`Figure_4.3_AI_Studio_Comparison.png`](file:///d:/projects/KD/SIH26090/photos/Figure_4.3_AI_Studio_Comparison.png) and [`Figure_4.7_Mobile_AI_Studio.png`](file:///d:/projects/KD/SIH26090/photos/Figure_4.7_Mobile_AI_Studio.png).

---

### Step 3 (1:45 – 2:45): Multilingual Voice Cataloging with Confirmation Gate
- **Action**: Open Voice Assistant (`/voice`).
- **Feature Demonstrated**:
  - Tap microphone and speak naturally in an Indian language (e.g., Tamil: *"இது தூய காஞ்சிபுரம் பட்டுப் புடவை, கோர்வை பார்டர், மூன்று நாட்கள் நெய்தது"* or Hindi: *"यह चन्नापटना की प्राकृतिक लकड़ी का खिलौना है"*).
  - Multilingual ASR transcribes the audio across 8 supported Indian languages (`ta`, `hi`, `te`, `kn`, `ml`, `bn`, `mr`, `en`).
  - NLP entity extraction automatically derives title, category (`handloom-textiles`), primary materials (`Mulberry Silk`), and estimated production time (`48 hours`).
  - **Strict Safety Rule**: The AI **never auto-publishes**. It presents an editable summary in the artisan's mother tongue. The artisan reviews and confirms before any record is created.
- **Reference**: See [`Figure_4.4_Mobile_Voice_Catalog.png`](file:///d:/projects/KD/SIH26090/photos/Figure_4.4_Mobile_Voice_Catalog.png).

---

### Step 4 (2:45 – 3:30): Explainable Living-Wage Pricing Engine
- **Action**: Navigate to Pricing Assistant.
- **Feature Demonstrated**:
  - Shows the transparent cost breakdown:
    $$\text{Fair Price} = \text{Raw Materials} + (\text{Labor Hours} \times \text{Regional Skilled Living Wage}) + \text{Tool Amortization} + \text{Fair Artisan Margin}$$
  - Transparent *"Why this price"* explanation shows raw materials (₹4,200) + 48 hours labor at ₹145/hour (₹6,960) + 20% sustainable margin = ₹13,392.
  - Artisan can adjust or override the suggested price. Any override is recorded in an audit log to continuously tune regional models without overriding artisan agency.
- **Reference**: See [`Figure_4.5_Pricing_Calculator_Result.png`](file:///d:/projects/KD/SIH26090/photos/Figure_4.5_Pricing_Calculator_Result.png).

---

### Step 5 (3:30 – 4:15): Buyer Discovery & Cryptographic Ed25519 Provenance Verification
- **Action**: Open Buyer Web (`http://localhost:3000`).
- **Feature Demonstrated**:
  - Browse craft heritage clusters: Kanchipuram Silk, Channapatna Toys, Bastar Dhokra.
  - Click on *"Kanchipuram Temple Border Pure Mulberry Silk Saree"*.
  - View **Ed25519 Provenance Badge**: Scan or click the QR code to open the public verification page (`/heritage/verify/{qr_hash}`).
  - Verification endpoint proves the cryptographic signature:
    - Master artisan identity verified: Meenakshi Ammal
    - Origin: Kanchipuram, Tamil Nadu (GI-001)
    - Signature: Valid Ed25519 public key signature matching CraftLens Root Authority.
  - Place Order: Seamless Razorpay UPI checkout in test mode; automatic order state transition to `CONFIRMED` and carrier tracking via Shiprocket sandbox.

---

### Step 6 (4:15 – 5:00): Admin Governance & DPDP Act 2023 Compliance
- **Action**: Open Admin Web (`http://localhost:3001`) logged in as `admin@craftlens.org`.
- **Feature Demonstrated**:
  - **Artisan KYC Queue**: Review submitted government artisan card (Pehchan card) and approve verification status.
  - **GI Claim Moderation**: Review Geographical Indication documentation before approving the authentic GI origin tag.
  - **DPDP Act 2023 Audit Trail**: Inspect tamper-evident audit logs recording user consents, consent withdrawals, and administrative approvals.
  - **Real-Time Observability**: Open `http://localhost:8000/api/v1/metrics` showing live Prometheus metrics (RPS, latencies, AI job counters).

---

## Offline / Fallback Presentation Plan

If internet or local emulator is restricted during judging:
1. The backend operates entirely with zero external network access using SQLite (`craftlens_dev.db`) and fallback deterministic NLP/pricing models.
2. High-resolution screenshots and HTML mockups in `photos/` and `photos/templates/` can be opened directly in any browser.
3. Database backup and restore can be verified in 3 seconds: `python scripts/backup_db.py --drill`.

