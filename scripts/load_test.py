"""Local load benchmark for CraftLens FastAPI backend at 100 and 500 concurrent requests.

Starts a local uvicorn instance in a child subprocess, waits for /api/v1/health,
executes async concurrency bursts via httpx, reports p50/p95/p99 latencies & RPS,
and cleanly terminates the server.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, math.ceil((pct / 100.0) * len(sorted_vals)) - 1))
    return round(sorted_vals[idx], 2)


async def _run_burst(base_url: str, path: str, concurrency: int) -> dict:
    limits = httpx.Limits(max_connections=max(concurrency, 100), max_keepalive_connections=100)
    latencies_ms: list[float] = []
    errors = 0

    async with httpx.AsyncClient(base_url=base_url, limits=limits, timeout=15.0) as client:
        # Warm cache with 1 request first on catalog endpoint
        await client.get(path)

        async def _one():
            nonlocal errors
            t0 = time.perf_counter()
            try:
                r = await client.get(path)
                if r.status_code != 200:
                    errors += 1
            except Exception:
                errors += 1
            finally:
                latencies_ms.append((time.perf_counter() - t0) * 1000.0)

        t_start = time.perf_counter()
        await asyncio.gather(*[_one() for _ in range(concurrency)])
        total_sec = max(0.001, time.perf_counter() - t_start)

    latencies_ms.sort()
    return {
        "endpoint": path,
        "concurrency": concurrency,
        "total_time_s": round(total_sec, 3),
        "rps": round(concurrency / total_sec, 1),
        "errors": errors,
        "error_rate_pct": round((errors / concurrency) * 100.0, 2),
        "p50_ms": _percentile(latencies_ms, 50),
        "p95_ms": _percentile(latencies_ms, 95),
        "p99_ms": _percentile(latencies_ms, 99),
    }


async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    backend_dir = root / "backend"
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=str(backend_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        # Wait up to 15s for uvicorn readiness
        async with httpx.AsyncClient(base_url=base_url, timeout=2.0) as probe:
            for _ in range(60):
                try:
                    r = await probe.get("/api/v1/health")
                    if r.status_code == 200:
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.25)

        results = []
        for path in ("/api/v1/health", "/api/v1/marketplace/products?page=1&page_size=20"):
            for n in (100, 500):
                results.append(await _run_burst(base_url, path, n))

        print(json.dumps({"base_url": base_url, "benchmarks": results}, indent=2))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
