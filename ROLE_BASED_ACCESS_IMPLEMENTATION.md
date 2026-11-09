# CraftLens 2.0: Role-Based Access Control (RBAC) & Artisan Onboarding

This document provides a technical overview of the Role-Based Access Control (RBAC) system, the Buyer-to-Artisan onboarding workflow, database migrations, security controls, and dual-experience mobile architecture implemented in **CraftLens 2.0**.

---

## 1. System Architecture

CraftLens supports two distinct user experiences inside a unified platform architecture:

```
                                  +------------------------------+
                                  |     Public Registration      |
                                  | (Strictly RETAIL_BUYER Role) |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  |       Buyer Dashboard        |
                                  | - Product Marketplace        |
                                  | - Orders & Tracking          |
                                  | - Buyer Profile              |
                                  +--------------+---------------+
                                                 |
                                      "Become an Artisan"
                                                 |
                                                 v
                                  +------------------------------+
                                  |  Artisan Application Form    |
                                  |  (Status: PENDING)           |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  |  Admin Dashboard / Review    |
                                  |  - Audit GI & Craft Lineage  |
                                  +-------+--------------+-------+
                                          |              |
                                [Approve] |              | [Reject]
                                          v              v
                  +-------------------------------+  +-------------------------------+
                  | Atomic DB Role Conversion:    |  | Application Status: REJECTED  |
                  | - Buyer Role Removed          |  | - Buyer Role Unchanged        |
                  | - ARTISAN Role Assigned       |  | - Reviewer Note Stored        |
                  | - ArtisanProfile Created      |  | - Re-application Permitted    |
                  | - Audit Log Recorded          |  +-------------------------------+
                  +---------------+---------------+
                                  |
                                  v
                  +-------------------------------+
                  |       Artisan Workspace       |
                  | - Artisan Dashboard & Sales   |
                  | - AI Studio (rembg, CLAHE)    |
                  | - Voice Cataloging (Bhashini) |
                  | - Explainable Pricing Engine  |
                  | - Inventory & Orders          |
                  +-------------------------------+
```

---

## 2. Role Descriptions & Hierarchy

| Role Code | Role Name | Scope & Permissions | Public Registration? |
|---|---|---|---|
| `RETAIL_BUYER` | Retail Consumer | Browses marketplace, places orders, views tracking, applies to become an artisan. | **Default on registration** |
| `WHOLESALE_BUYER` | B2B / Wholesale Buyer | Browses catalog, submits RFQs, generates purchase orders, bulk procurement. | Public registration allowed |
| `ARTISAN` | Traditional Artisan | Manages craft inventory, AI Studio photo processing, voice cataloging, pricing engine. | **Restricted** (Requires Admin Approval) |
| `ADMIN` | System Administrator | Platform governance, audits artisan applications, approves/rejects credentials, monitors DPDP logs. | **Restricted** (Pre-seeded / Managed) |

---

## 3. Buyer-to-Artisan Application Workflow

1. **Submission**:
   - A logged-in buyer navigates to **Profile > "Become an Artisan"**.
   - Fills out: Full Name, Craft Specialization, Years of Experience, City, State, Craft Description & Lineage, optional Portfolio URL, and Supporting Documents URL.
   - Client sends `POST /api/v1/artisan-applications/me`.
   - Backend verifies the user is not already an artisan and does not have a duplicate pending application.
   - Application record is created with `status="PENDING"`.
   - **Crucial Rule**: The user's role remains `RETAIL_BUYER`. No artisan privileges are granted at submission.

2. **Admin Review & Decision**:
   - Administrator opens the Admin Governance Portal (`http://localhost:3001` or `admin-web`).
   - Filters applications by `PENDING`, `APPROVED`, or `REJECTED`.
   - Reviews applicant's craft experience, lineage description, portfolio, and location.
   - Enters optional reviewer notes.
   - **On Approval** (`POST /api/v1/artisan-applications/admin/{id}/approve`):
     - Executes inside an atomic database transaction.
     - Strips buyer role (`RETAIL_BUYER` / `WHOLESALE_BUYER`).
     - Appends `ARTISAN` role.
     - Creates or updates the user's `ArtisanProfile`.
     - Sets application status to `APPROVED`, records admin ID and review timestamp.
     - Writes immutable `AuditLog` entry.
   - **On Rejection** (`POST /api/v1/artisan-applications/admin/{id}/reject`):
     - Sets application status to `REJECTED`.
     - Retains user's Buyer role intact.
     - Allows user to submit a revised application with updated documentation.

3. **Client Activation**:
   - On the mobile application, the user clicks **Check Approval Status** or signs in again.
   - The updated JWT session carries the `ARTISAN` role.
   - The app unlocks the full Artisan suite (`/(tabs)`: Dashboard, AI Studio, Voice AI, Pricing, Orders).

---

## 4. Database Schema Changes

### 4.1 New Table: `artisan_applications`

```sql
CREATE TABLE artisan_applications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    craft_specialization VARCHAR(255) NOT NULL,
    experience_years INTEGER NOT NULL DEFAULT 1,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    portfolio_url VARCHAR(500),
    craft_description TEXT NOT NULL,
    supporting_documents_url VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    reviewer_notes TEXT,
    reviewed_by_user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX ix_artisan_applications_user_id ON artisan_applications(user_id);
CREATE INDEX ix_artisan_applications_status ON artisan_applications(status);
```

### 4.2 Alembic Migration

- **Revision ID**: `b2d4f6e8a012`
- **Down Revision**: `a8c298840ad8`
- **File**: `backend/alembic/versions/b2d4f6e8a012_artisan_applications.py`

---

## 5. API Endpoint Documentation

| Method | Endpoint | Access Role | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Registers buyer account (defaults to `RETAIL_BUYER`). Rejects `ARTISAN` or `ADMIN` with HTTP 400. |
| `POST` | `/api/v1/auth/login` | Public | OAuth2 password flow; issues JWT tokens and reveals approved roles. |
| `POST` | `/api/v1/artisan-applications/me` | Logged In Buyer | Submits artisan application. Prevents duplicate pending applications. |
| `GET` | `/api/v1/artisan-applications/me` | Logged In Buyer | Retrieves latest application status for current user. |
| `GET` | `/api/v1/artisan-applications/admin` | `ADMIN` | Lists applications with optional `?status=PENDING\|APPROVED\|REJECTED` filter. |
| `POST` | `/api/v1/artisan-applications/admin/{id}/approve` | `ADMIN` | Approves application, converts role to `ARTISAN`, initializes profile, logs audit. |
| `POST` | `/api/v1/artisan-applications/admin/{id}/reject` | `ADMIN` | Rejects application with notes, keeps buyer role unchanged. |
| `POST` | `/api/v1/studio/analyze` | `ARTISAN` | Analyzes photo blur and lighting. 403 for buyers. |
| `POST` | `/api/v1/studio/process` | `ARTISAN` | Background removal and studio staging. 403 for buyers. |
| `POST` | `/api/v1/pricing/calculate` | `ARTISAN` | Fair pricing calculation. 403 for buyers. |
| `GET` | `/api/v1/business/metrics` | `ARTISAN` | Artisan revenue, sales, and inventory analytics. 403 for buyers. |

---

## 6. Security & Defense-in-Depth

1. **Role Enforcement on Every Endpoint**:
   - Enforced at the FastAPI dependency level via `Depends(require_role("ARTISAN"))` / `Depends(require_role("ADMIN"))`.
   - Redundantly checked inside handlers (`require_role(...)(current_user)`) for total immunity against routing bypasses.
2. **Untrusted Frontend Roles**:
   - The frontend role parameter is never trusted. Registration strictly validates and overrides inputs.
   - Applications must pass admin scrutiny before database role mutation.
3. **Atomic State Mutation**:
   - Application status change and role reassignment execute in a single SQLAlchemy database transaction, preventing partial upgrades.
4. **Audit Logging**:
   - Every approval and rejection generates an immutable `AuditLog` entry storing the administrator ID, resource target, and timestamp.
5. **Route-Level Mobile Protection**:
   - `mobile/app/(tabs)/_layout.tsx` validates user authentication and role before rendering any artisan screens. Non-artisans are redirected to `/(buyer-tabs)/marketplace`.

---

## 7. Migration Commands

To apply database migrations to your SQLite or PostgreSQL database:

```bash
# Navigate to backend
cd backend

# Run migration upgrade to head
python -m alembic upgrade head
```

To rollback:
```bash
python -m alembic downgrade -1
```

---

## 8. Mobile Environment Configuration

The mobile app supports both experiences in a single codebase with role-based routing:

```
mobile/
├── app/
│   ├── (buyer-tabs)/          # Buyer Experience Suite
│   │   ├── _layout.tsx        # Buyer Bottom Navigation (Explore, Orders, Profile)
│   │   ├── marketplace.tsx    # Craft Browsing, Search, Filters, Detail Modal
│   │   ├── orders.tsx         # Buyer Order Tracking
│   │   ├── profile.tsx        # Buyer Info & "Become an Artisan" Status Card
│   │   └── apply-artisan.tsx  # Artisan Application Form
│   ├── (tabs)/                # Artisan Experience Suite (Role Guarded)
│   │   ├── _layout.tsx        # Guards route to ARTISAN only
│   │   ├── index.tsx          # Artisan Sales Dashboard
│   │   ├── studio.tsx         # AI Photo Staging
│   │   ├── voice.tsx          # Regional Voice Cataloging
│   │   ├── pricing.tsx        # Explainable Fair Pricing
│   │   ├── orders.tsx         # B2B & Fulfillment
│   │   └── profile.tsx        # Artisan Heritage Profile
│   ├── login.tsx              # Authenticates and routes to /(tabs) or /(buyer-tabs)
│   └── register.tsx           # Registers buyer and routes to /(buyer-tabs)/marketplace
```

### Running Mobile App

```bash
cd mobile
npm install
npm run start
```

---

## 9. Testing Instructions

CraftLens contains a 34-test automated suite covering all RBAC scenarios and functional phases:

```bash
cd backend
python -m pytest tests/test_rbac_and_applications.py -v
```

### Test Scenarios Verified:
1. Buyer registration defaults to `RETAIL_BUYER`.
2. Public registration rejects `ARTISAN` or `ADMIN` with HTTP 400.
3. Buyer submits artisan application (`status="PENDING"`).
4. Duplicate pending application is rejected with HTTP 400.
5. Submitting application leaves buyer role unchanged.
6. Buyer is denied access to artisan endpoints (HTTP 403 Forbidden).
7. Non-admin cannot list or approve applications (HTTP 403 Forbidden).
8. Admin can list applications with `?status=PENDING` filter.
9. Admin approval atomically converts role to `ARTISAN`, initializes profile, logs audit.
10. Approved artisan can access protected studio and pricing endpoints.
11. Admin rejection sets status `REJECTED` and preserves Buyer role.
12. Rejected buyer can submit a revised artisan application.

To run the complete platform test suite:
```bash
cd backend
python -m pytest tests -v
```

---

## 10. Deployment Instructions

### Backend (FastAPI + Uvicorn)
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Admin Web Portal (Next.js)
```bash
cd admin-web
npm install
npm run dev
# Accessible at http://localhost:3001
```

### Pre-seeded Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@craftlens.org` | `CraftLensAdmin@2026` |
| Demonstration Artisan | `artisan@craftlens.org` | `Artisan@2026` |
| New Buyers | Self-registered via app | User defined |
