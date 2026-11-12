"""CraftLens 2.0 AI Microservice.

Dedicated FastAPI service for computer vision photo analysis/enhancement and
multilingual speech/catalog extraction (invoked by backend or Celery workers).
"""

from __future__ import annotations

import os

from fastapi import FastAPI

app = FastAPI(
    title="CraftLens AI Service",
    version="2.0.0",
    description="Vision studio & multilingual catalog microservice.",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Service liveness check."""
    return {
        "status": "ok",
        "service": "craftlens-ai-service",
        "asr_fallback": os.getenv("ASR_FALLBACK", "whisper_local"),
    }
