# CraftLens 2.0 — Performance, Scalability & Load Evaluation

**Benchmarked against:** Local standalone Uvicorn process running CraftLens FastAPI 2.0 with SQLite / Alembic (`f6b8d0e2c456`) and TTL caching.  
**Benchmark Script:** `python scripts/load_test.py` (burst concurrency using `httpx.AsyncClient` with connection pooling)

---

## 1. Concurrency Benchmarks (100 and 500 Concurrent Requests)

| Endpoint | Concurrency (Burst) | Total Time | RPS | Error Rate | p50 Latency | p95 Latency | p99 Latency |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/api/v1/health` | 100 | 1.168 s | 85.6 req/s | 0.0% (0 errors) | 780.15 ms | 1086.37 ms | 1098.31 ms |
| `/api/v1/health` | 500 | 8.339 s | 60.0 req/s | 0.0% (0 errors) | 4,590.59 ms | 7,951.88 ms | 8,160.30 ms |
| `/api/v1/marketplace/products?page=1&page_size=20` | 100 | 0.752 s | 133.0 req/s | 0.0% (0 errors) | 327.16 ms | 647.63 ms | 667.76 ms |
| `/api/v1/marketplace/products?page=1&page_size=20` | 500 | 7.770 s | 64.4 req/s | 0.0% (0 errors) | 3,225.04 ms | 7,217.74 ms | 7,576.92 ms |

### Key Observations & Optimizations Implemented:
1. **N+1 Query Elimination:** `marketplace.discover_products` uses `selectinload` for `variants`, `images`, and `category`, plus `joinedload` on `artisan.user`, collapsing what was previously 15+ sub-queries into 2 indexed queries.
2. **Caching:** `CraftCache` (`backend/app/core/cache.py`) serves identical catalog pages from Redis if `REDIS_URL` is configured, or an in-memory thread-safe TTL cache (45s TTL), achieving 133 RPS with sub-650ms p95 under 100 concurrent requests on a single worker.
3. **Database Indexes:** Alembic migration `f6b8d0e2c456` added compound performance indexes:
   - `ix_products_status_created_at` on `products(status, created_at)`
   - `ix_products_gi_verification_status` on `products(gi_verification_status)`
   - `ix_orders_buyer_created_at` on `orders(buyer_id, created_at)`
   - `ix_audit_logs_created_at` on `audit_logs(created_at)`

---

## 2. Web Frontend Audits & Lighthouse Targets

### Buyer Web (`buyer-web`)
- **Next.js Version:** 15.5.29 (production standalone output ready)
- **Static Pages Pre-rendered:** 16 static pages (`/`, `/catalog`, `/origins`, `/b2b`, `/cart`, `/login`, `/register`, `/sitemap.xml`, `/robots.txt`, etc.)
- **First Load JS:** 102 kB shared bundle; catalog route 120 kB.
- **Images:** Migrated `<img>` tags on catalog product cards to `next/image` with responsive `sizes` attribute and layout blur placeholders.
- **Structured Data:** Injected Schema.org `ItemList` + `Product` JSON-LD for rich Google search indexing.
- **i18n Coverage:** Language switching toolbar supporting 8 languages (`en`, `hi`, `ta`, `te`, `kn`, `ml`, `bn`, `mr`) in `src/lib/i18n.ts`.

### Admin Web (`admin-web`)
- **Production Build:** `next build` generates 111 kB optimized bundle; 0 ESLint errors/warnings.
- **Live Queues:** Connected to live backend APIs for Artisan Applications, Seller KYC Verifications, GI Claim Moderation, and DPDP Audit Log overview.

### Lighthouse Environment Availability & Shortfall Plan:
- **Headless Chrome / Lighthouse CLI:** The development environment is a sandboxed Windows shell without Google Chrome or `@lhci/cli` installed.
- **Target Metrics for Staging Deployment:**
  - Performance: Target `>= 85` (mitigated by SSG pre-rendering, `next/image` WebP encoding, and 102 kB bundle).
  - Accessibility: Target `>= 95` (mitigated by accessible contrast `#565C55` / `#285C45` >= 4.5:1, `aria-label` attributes on icon buttons, semantic `<main>`, `<nav>`, `<footer>`).
  - Best Practices: Target `>= 90` (OWASP security headers `nosniff`, `DENY`, strict CSP, HTTPS redirect).
  - SEO: Target `>= 90` (Schema.org JSON-LD, OpenGraph tags, sitemap.xml, robots.txt).
- **Remediation Plan for Production Host:** Run Lighthouse in GitHub Actions CI using `treosh/lighthouse-ci-action` on Linux runners where Chromium is readily containerized.
