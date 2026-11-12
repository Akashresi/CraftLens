# CraftLens 2.0 – Production Operations Runbook

This runbook defines the operational procedures for deploying, maintaining, monitoring, and recovering the CraftLens platform in staging and production environments.

---

## 1. Architecture & Service Topology

| Service | Port | Base Path | Health Check | Metrics | Non-Root User |
|---|---|---|---|---|---|
| **backend** (FastAPI) | 8000 | `/api/v1` | `GET /api/v1/health`, `GET /api/v1/ready` | `GET /api/v1/metrics` | `appuser` (10001) |
| **buyer-web** (Next.js 15) | 3000 | `/` | `GET /` | Built-in Next.js | `nextjs` (10001) |
| **admin-web** (Next.js 15) | 3001 | `/` | `GET /` | Built-in Next.js | `nextjs` (10001) |
| **ai-service** (Queue Worker) | 8001 / async | Internal | Internal health loop | Task counter metrics | `appuser` (10001) |
| **postgres** (Database) | 5432 | TCP | `pg_isready -U postgres` | Postgres Exporter | `postgres` (999) |
| **redis** (Cache & Job Broker) | 6379 | TCP | `redis-cli ping` | Redis Exporter | `redis` (999) |

---

## 2. Health & Readiness Probes

### Liveness Probe (`GET /api/v1/health`)
- Returns `HTTP 200` with `{"status": "ok", "app": "CraftLens", "version": "2.0.0"}`.
- Used by orchestrators (Kubernetes / Docker Swarm / AWS ECS) to detect hung workers.

### Readiness Probe (`GET /api/v1/ready`)
- Checks connectivity to:
  1. **Database**: Executes `SELECT 1` on the active SQLAlchemy engine.
  2. **Upload Storage**: Verifies write and removal permissions in `uploads/`.
  3. **Redis Cache / Queue**: Pings Redis if configured (`REDIS_URL`).
- Returns:
  - `HTTP 200`: `{"status": "ready", "database": "connected", "storage": "writable", "redis": "connected|disabled"}`.
  - `HTTP 503`: If any required dependency is unreachable. Traffic is stopped before routing to unready instances.

---

## 3. Zero-Downtime Deployment Procedure

### Blue/Green Rolling Container Updates
1. **Pre-flight Check**:
   ```bash
   # Run automated migration idempotency check
   python -m pytest backend/tests/test_migrations_reversible.py -v
   ```
2. **Apply Backward-Compatible Database Migrations**:
   ```bash
   cd backend && python -m alembic upgrade head && cd ..
   ```
   *Note: In CraftLens, schema migrations must follow the expand-contract pattern. Never drop columns or rename columns used by the running blue version.*
3. **Pull and Deploy New Green Image**:
   ```bash
   docker compose pull backend buyer-web admin-web
   docker compose up -d --no-deps --build --scale backend=2 backend
   ```
4. **Readiness Verification**:
   Poll `http://localhost:8000/api/v1/ready` until `HTTP 200` is returned with status `"ready"`.
5. **Retire Blue Containers**:
   ```bash
   docker compose up -d --no-deps --scale backend=1 backend
   ```

---

## 4. Database Backup, SHA-256 Verification & Restore Drills

Automated backups are managed via `scripts/backup_db.py`.

### Scheduled Backup Command
```bash
python scripts/backup_db.py --out backups/
```
The script generates:
- Compressed database snapshot: `craftlens_backup_<timestamp>.db.gz` or `.sql.gz`
- SHA-256 verification manifest: `craftlens_backup_<timestamp>.sha256`

### Automated Recovery & Integrity Drill
To verify that existing backups are uncorrupted and can be restored without data loss:
```bash
python scripts/backup_db.py --drill
```
**Drill Steps Performed Automatically**:
1. Creates an isolated test database with active Alembic migrations.
2. Seeds core relational test records (users, products, orders).
3. Executes a full backup snapshot and computes the SHA-256 checksum.
4. Restores into a blank sandboxed drill database.
5. Verifies SHA-256 integrity and executes count queries on all tables.
6. Cleans up temporary artifacts and reports drill success.

---

## 5. Secret Rotation Protocol

All secrets are injected exclusively through environment variables.

### A. JWT & Session Signing Key (`SECRET_KEY`)
1. Generate a high-entropy 256-bit secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
2. During zero-downtime rotation, configure the backend to accept signatures signed with `OLD_SECRET_KEY` while issuing tokens with `NEW_SECRET_KEY` for a 24-hour grace period.
3. Update `.env` / AWS Secrets Manager / Vault and restart backend containers.

### B. Ed25519 Provenance Signing Keypair (`PROVENANCE_PRIVATE_KEY_PEM`)
1. Generate a new Ed25519 keypair:
   ```bash
   python -c "from cryptography.hazmat.primitives.asymmetric import ed25519; from cryptography.hazmat.primitives import serialization; key = ed25519.Ed25519PrivateKey.generate(); print(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode())"
   ```
2. Update the public key registry: The backend provenance verifier supports historical key rotation by storing public keys in `backend/app/core/security.py` or database key registries.
3. Replace `PROVENANCE_PRIVATE_KEY_PEM` in production environment variables.

### C. Payment Gateway (`RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`)
1. Log in to Razorpay Dashboard -> Settings -> API Keys.
2. Generate new Secret Key.
3. Update webhook signature secret in Razorpay Webhooks settings and server `.env`.
4. Run test webhook verification to ensure `craftlens.app.api.v1.endpoints.orders.verify_webhook_signature` succeeds.
5. Revoke the old key.

---

## 6. Incident Response Playbook

### Incident Severity Levels
- **P1 (Critical)**: Platform down, checkout/payment failure, data breach, corrupted database. SLA: 15 min acknowledge, 1 hour mitigate.
- **P2 (Major)**: AI Studio degradation, slow search latency (>2s), single carrier API failure. SLA: 1 hour acknowledge, 4 hours mitigate.
- **P3 (Minor)**: UI cosmetic glitch, non-blocking admin filter issue. SLA: 24 hours.

### Playbook: Payment Webhook Signature Failure / Missed Webhooks
1. **Symptom**: Orders remain in `placed` status despite successful customer debit; webhook errors logged in Prometheus (`craftlens_http_requests_total{status="400", endpoint="/orders/webhook"}`).
2. **Diagnosis**:
   - Check structured logs for: `JSON {"event": "request_completed", "status_code": 400, "path": "/api/v1/orders/webhook"}`.
   - Verify `RAZORPAY_WEBHOOK_SECRET` matches Razorpay dashboard.
3. **Mitigation**:
   - Manually trigger payment reconciliation:
     ```bash
     # Inspect order status via backend admin CLI or endpoint
     curl -X GET "http://localhost:8000/api/v1/orders/{order_id}" -H "Authorization: Bearer <ADMIN_TOKEN>"
     ```
   - In Razorpay dashboard, navigate to Webhooks -> Retry Failed Events. The idempotency check ensures duplicate events are skipped safely without duplicate inventory deductions.

### Playbook: Account Lockout Spike / Credential Stuffing
1. **Symptom**: Multiple users locked out; high rate of `429 Too Many Requests` or `401 Unauthorized` on `/api/v1/auth/login`.
2. **Diagnosis**:
   - Check Prometheus rate limit metrics: `craftlens_auth_failures_total`.
3. **Mitigation**:
   - An artisan locked out after 5 invalid attempts will automatically be unlocked after 15 minutes (`ACCOUNT_LOCKOUT_MINUTES`).
   - Admin unlock: Query user by email and reset `failed_login_attempts = 0` and `locked_until = None`.

---

## 7. Rollback Procedure

If a bad deployment is identified:
1. **Rollback Container Image**:
   ```bash
   docker compose pull craftlens/backend:previous-stable
   docker compose up -d backend
   ```
2. **Rollback Database Migration (if required)**:
   ```bash
   cd backend
   # Check current migration revision
   python -m alembic current
   # Downgrade 1 revision safely
   python -m alembic downgrade -1
   cd ..
   ```
3. **Verify Health**:
   ```bash
   curl -f http://localhost:8000/api/v1/ready
   ```

---

## 8. Prometheus Metrics & Grafana Dashboard

### Prometheus Scrape Configuration
Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: "craftlens-backend"
    scrape_interval: 15s
    metrics_path: "/api/v1/metrics"
    static_configs:
      - targets: ["backend:8000"]
```

### Key Metrics Exposed
- `craftlens_http_requests_total{method, endpoint, status}`: Total HTTP requests by path and HTTP code.
- `craftlens_http_request_duration_seconds{method, endpoint}`: Latency percentiles (p50, p90, p99).
- `craftlens_ai_jobs_total{job_type, status}`: Completed, pending, and failed background AI jobs.
- `craftlens_active_users`: Real-time session gauge.

### Grafana Dashboard Import
1. Navigate to Grafana -> Dashboards -> Import.
2. Upload `deploy/grafana/dashboards/craftlens_overview.json`.
3. Select your Prometheus data source. The dashboard visualizes Request Volume, Error Rates (4xx/5xx), p95 Latencies, and AI Processing throughput.

