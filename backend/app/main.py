import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.observability import init_sentry, logger, metrics, setup_structured_logging

setup_structured_logging()
init_sentry()

UPLOAD_DIR = settings.LOCAL_UPLOAD_DIR or "./uploads"
os.makedirs(f"{UPLOAD_DIR}/original", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/processed", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Production API for CraftLens 2.0 - AI-Powered Artisan Business Management and Global Marketplace Platform.",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)


@app.middleware("http")
async def security_headers_and_csrf_middleware(request: Request, call_next) -> Response:
    """Enforces X-Request-ID tracking, OWASP security headers, and double-submit CSRF protection."""
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = req_id
    start_time = time.perf_counter()

    # CSRF check applies when session cookie is used without an explicit Bearer token
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        has_session_cookie = "craftlens_session" in request.cookies
        has_bearer = request.headers.get("authorization", "").lower().startswith("bearer ")
        if has_session_cookie and not has_bearer:
            csrf_cookie = request.cookies.get("craftlens_csrf")
            csrf_header = request.headers.get("x-csrf-token")
            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token missing or invalid"},
                    headers={"X-Request-ID": req_id},
                )

    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"
    if not request.url.path.startswith(f"{settings.API_V1_STR}/docs"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data: https:; frame-ancestors 'none'"
        )
    if settings.APP_ENV.lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    client_ip = request.client.host if request.client else "unknown"
    metrics.record_request(request.method, request.url.path, response.status_code, duration_ms / 1000.0)
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
        extra={
            "request_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
        },
    )
    return response
    return response


# Strict CORS allowlist (never wildcard '*')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Request-ID"],
)

# Static media serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include master API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
        "status": "operational",
    }
