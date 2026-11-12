"""Sliding-window rate limiter for authentication, uploads, and AI endpoints."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding-window rate limiter keyed by (scope, client_ip)."""

    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Clears all rate-limit buckets (for isolated testing)."""
        with self._lock:
            self._buckets.clear()

    def check(self, key: str, max_requests: int, window_seconds: int) -> None:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= max_requests:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Retry after {retry_after}s.",
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)


rate_limiter = SlidingWindowRateLimiter()


def rate_limit(scope: str, max_requests: int, window_seconds: int = 60):
    """FastAPI dependency enforcing rate limits per client IP and endpoint scope."""

    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        rate_limiter.check(f"{scope}:{client_ip}", max_requests=max_requests, window_seconds=window_seconds)

    return dependency
