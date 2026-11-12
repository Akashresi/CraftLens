"""Observability, structured JSON logging, Sentry hook, and Prometheus metrics for CraftLens 2.0."""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings


class JsonLogFormatter(logging.Formatter):
    """Outputs standardized JSON log records with ISO timestamps and contextual request metadata."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for attr in ("request_id", "method", "path", "status_code", "duration_ms", "client_ip"):
            val = getattr(record, attr, None)
            if val is not None:
                payload[attr] = val
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_structured_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


def init_sentry() -> bool:
    """Initializes Sentry SDK if SENTRY_DSN is configured. Graceful no-op if unset."""
    dsn = settings.SENTRY_DSN or os.getenv("SENTRY_DSN", "")
    if not dsn:
        return False
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            environment=settings.APP_ENV,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
        )
        return True
    except Exception:
        return False


class PrometheusMetrics:
    """Lightweight in-memory Prometheus-compatible metrics registry (avoids heavy native C extensions)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requests: dict[tuple[str, str, int], int] = {}
        self._latencies: dict[str, list[float]] = {}
        self._ai_jobs: dict[str, int] = {}

    def record_request(self, method: str, path: str, status_code: int, duration_sec: float) -> None:
        key = (method.upper(), path, status_code)
        with self._lock:
            self._requests[key] = self._requests.get(key, 0) + 1
            path_key = path
            bucket = self._latencies.setdefault(path_key, [])
            if len(bucket) < 200:
                bucket.append(duration_sec)

    def record_ai_job(self, job_type: str, status: str) -> None:
        key = f"{job_type}:{status}"
        with self._lock:
            self._ai_jobs[key] = self._ai_jobs.get(key, 0) + 1

    def render_text(self) -> str:
        lines = [
            "# HELP craftlens_http_requests_total Total HTTP requests by method, route, and status",
            "# TYPE craftlens_http_requests_total counter",
        ]
        with self._lock:
            for (m, p, s), count in sorted(self._requests.items()):
                lines.append(f'craftlens_http_requests_total{{method="{m}",path="{p}",status="{s}"}} {count}')

            lines.append("# HELP craftlens_http_request_duration_seconds Average latency in seconds")
            lines.append("# TYPE craftlens_http_request_duration_seconds gauge")
            for p, durations in sorted(self._latencies.items()):
                avg = sum(durations) / len(durations) if durations else 0.0
                lines.append(f'craftlens_http_request_duration_seconds{{path="{p}"}} {avg:.4f}')

            lines.append("# HELP craftlens_ai_jobs_total AI jobs processed by type and outcome")
            lines.append("# TYPE craftlens_ai_jobs_total counter")
            for key, count in sorted(self._ai_jobs.items()):
                jtype, jstat = key.split(":", 1)
                lines.append(f'craftlens_ai_jobs_total{{job_type="{jtype}",status="{jstat}"}} {count}')

        lines.append("")
        return "\n".join(lines)


metrics = PrometheusMetrics()
logger = logging.getLogger("craftlens")
