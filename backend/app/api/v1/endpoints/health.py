import os
import tempfile

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.observability import metrics
from app.db.session import get_db
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Liveness probe validating basic process and database connectivity."""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version="2.0.0",
        app_name=settings.APP_NAME,
        database_connected=db_ok,
        ai_service_available=True,
    )


@router.get("/ready")
def readiness_probe(response: Response, db: Session = Depends(get_db)):
    """Kubernetes/Container readiness probe checking DB, storage writeability, and Redis."""
    checks: dict[str, bool] = {"database": False, "storage": False, "redis": True}

    # 1. Database read/write
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # 2. Local uploads storage writable
    try:
        upload_dir = settings.LOCAL_UPLOAD_DIR or "./uploads"
        os.makedirs(upload_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=upload_dir, delete=True) as tmp:
            tmp.write(b"ready_check")
        checks["storage"] = True
    except Exception:
        checks["storage"] = False

    # 3. Redis connectivity if configured
    if settings.REDIS_URL:
        try:
            import redis

            client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.5)
            client.ping()
            checks["redis"] = True
        except Exception:
            checks["redis"] = False

    redis_required = os.getenv("REDIS_REQUIRED", "false").lower() == "true"
    is_ready = checks["database"] and checks["storage"] and (checks["redis"] if redis_required else True)
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": os.getenv("DEPLOYMENT_TIMESTAMP", "2026-11-12"),
        "checks": checks,
    }


@router.get("/metrics")
def prometheus_metrics():
    """Exposes Prometheus text exposition format (version 0.0.4) for scraper ingestion."""
    content = metrics.render_text()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")
