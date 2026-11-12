"""Asynchronous AI job queue with Redis push + threadpool fallback, retries, and timeouts."""

from __future__ import annotations

import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import AIJob, ImageProcessingJob
from app.services.image_studio import (
    analyze_image_quality,
    correct_lighting_and_color,
    generate_lifestyle_background,
    generate_studio_white_background,
    remove_product_background,
)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="craftlens-ai")


def _try_push_redis(job_id: str, payload: dict) -> bool:
    """Enqueues job descriptor to Redis list if REDIS_URL is configured and reachable."""
    if not settings.REDIS_URL:
        return False
    try:
        import redis

        client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.5)
        client.rpush("craftlens:ai_jobs", json.dumps({"job_id": job_id, **payload}))
        return True
    except Exception:
        return False


def _run_studio_job_sync(
    job_id: str,
    raw_bytes: bytes,
    lifestyle_theme: str,
    upload_base: str,
    original_url: str,
    session_factory=SessionLocal,
    max_retries: int = 2,
    timeout_seconds: float = 30.0,
) -> None:
    db = session_factory()
    try:
        job = db.query(AIJob).filter(AIJob.id == job_id).first()
        if not job:
            return
        job.status = "PROCESSING"
        db.commit()

        last_err: str | None = None
        for attempt in range(1, max_retries + 2):
            try:
                start = time.time()

                def _work(start_ts: float = start, attempt_no: int = attempt) -> dict:
                    q = analyze_image_quality(raw_bytes)
                    lit = correct_lighting_and_color(raw_bytes)
                    trans = remove_product_background(lit)
                    white = generate_studio_white_background(trans)
                    life = generate_lifestyle_background(trans, theme=lifestyle_theme)

                    trans_path = f"{upload_base}/processed/{job_id}_transparent.png"
                    white_path = f"{upload_base}/processed/{job_id}_white.jpg"
                    life_path = f"{upload_base}/processed/{job_id}_lifestyle.jpg"
                    os.makedirs(f"{upload_base}/processed", exist_ok=True)
                    with open(trans_path, "wb") as f:
                        f.write(trans)
                    with open(white_path, "wb") as f:
                        f.write(white)
                    with open(life_path, "wb") as f:
                        f.write(life)

                    return {
                        "job_id": job_id,
                        "original_url": original_url,
                        "transparent_png_url": f"/uploads/processed/{job_id}_transparent.png",
                        "white_bg_url": f"/uploads/processed/{job_id}_white.jpg",
                        "lifestyle_url": f"/uploads/processed/{job_id}_lifestyle.jpg",
                        "quality_score": q["quality_score"],
                        "cropping_feedback": q["cropping_feedback"],
                        "latency_ms": int((time.time() - start_ts) * 1000),
                        "attempts": attempt_no,
                        "status": "COMPLETED",
                    }

                with ThreadPoolExecutor(max_workers=1) as inner:
                    res = inner.submit(_work).result(timeout=timeout_seconds)

                job.status = "COMPLETED"
                job.result = res
                db.add(
                    ImageProcessingJob(
                        id=job_id,
                        user_id=job.user_id,
                        original_image_url=original_url,
                        processed_image_url=res["white_bg_url"],
                        operation="FULL_STUDIO_PIPELINE_ASYNC",
                        status="COMPLETED",
                        latency_ms=res["latency_ms"],
                    )
                )
                db.commit()
                return
            except (FuturesTimeoutError, Exception) as exc:
                last_err = str(exc)
                time.sleep(0.05 * attempt)

        job.status = "FAILED"
        job.result = {"error": last_err or "Job failed after retries", "attempts": max_retries + 1}
        db.commit()
    finally:
        db.close()


def enqueue_studio_job(
    user_id: str,
    raw_bytes: bytes,
    lifestyle_theme: str,
    upload_base: str,
    original_url: str,
    db,
    session_factory=SessionLocal,
) -> AIJob:
    """Persists AIJob in QUEUED state, pushes to Redis if active, and dispatches local worker."""
    job_id = str(uuid.uuid4())
    redis_queued = _try_push_redis(job_id, {"job_type": "STUDIO_PROCESS", "theme": lifestyle_theme})

    job = AIJob(
        id=job_id,
        user_id=user_id,
        job_type="STUDIO_PROCESS",
        status="QUEUED",
        payload={"lifestyle_theme": lifestyle_theme, "original_url": original_url, "redis_queued": redis_queued},
        result={},
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    _EXECUTOR.submit(
        _run_studio_job_sync,
        job_id,
        raw_bytes,
        lifestyle_theme,
        upload_base,
        original_url,
        session_factory,
    )
    return job
