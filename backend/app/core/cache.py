"""Lightweight Redis cache with bounded in-memory TTL fallback for marketplace catalog reads."""

from __future__ import annotations

import json
import threading
import time
from typing import Any

from app.core.config import settings


class CraftCache:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._mem: dict[str, tuple[float, str]] = {}
        self._redis = None
        self._redis_checked = False

    def _get_redis(self):
        if self._redis_checked:
            return self._redis
        self._redis_checked = True
        if not settings.REDIS_URL:
            return None
        try:
            import redis

            client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0, decode_responses=True)
            client.ping()
            self._redis = client
        except Exception:
            self._redis = None
        return self._redis

    def get_json(self, key: str) -> Any | None:
        client = self._get_redis()
        if client is not None:
            try:
                raw = client.get(key)
                return json.loads(raw) if raw else None
            except Exception:
                pass
        now = time.monotonic()
        with self._lock:
            entry = self._mem.get(key)
            if not entry:
                return None
            expires_at, raw = entry
            if now > expires_at:
                del self._mem[key]
                return None
            return json.loads(raw)

    def set_json(self, key: str, value: Any, ttl_seconds: int = 45) -> None:
        serialized = json.dumps(value, default=str)
        client = self._get_redis()
        if client is not None:
            try:
                client.setex(key, ttl_seconds, serialized)
                return
            except Exception:
                pass
        with self._lock:
            if len(self._mem) > 512:
                self._mem.clear()
            self._mem[key] = (time.monotonic() + ttl_seconds, serialized)

    def invalidate_prefix(self, prefix: str) -> None:
        client = self._get_redis()
        if client is not None:
            try:
                keys = list(client.scan_iter(match=f"{prefix}*"))
                if keys:
                    client.delete(*keys)
            except Exception:
                pass
        with self._lock:
            stale = [k for k in self._mem if k.startswith(prefix)]
            for k in stale:
                del self._mem[k]


cache = CraftCache()
