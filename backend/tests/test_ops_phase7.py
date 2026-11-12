"""Tests for Phase 7 Operations, Health, Readiness, and Observability."""

import httpx


async def test_health_liveness_endpoint(async_client: httpx.AsyncClient) -> None:
    resp = await async_client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "CraftLens" in data["app_name"]
    assert data["version"] == "2.0.0"


async def test_readiness_probe_endpoint(async_client: httpx.AsyncClient) -> None:
    resp = await async_client.get("/api/v1/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] is True
    assert data["checks"]["storage"] is True


async def test_prometheus_metrics_exposition(async_client: httpx.AsyncClient) -> None:
    # Trigger an endpoint so metrics are populated
    await async_client.get("/api/v1/health")

    resp = await async_client.get("/api/v1/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")
    content = resp.text
    assert "craftlens_http_requests_total" in content
    assert "craftlens_http_request_duration_seconds" in content
    assert "craftlens_ai_jobs_total" in content


async def test_x_request_id_header_propagation(async_client: httpx.AsyncClient) -> None:
    # Custom request id
    resp = await async_client.get("/api/v1/health", headers={"X-Request-ID": "custom-trace-12345"})
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID") == "custom-trace-12345"

    # Generated request id
    resp2 = await async_client.get("/api/v1/health")
    assert resp2.status_code == 200
    assert "X-Request-ID" in resp2.headers
    assert len(resp2.headers["X-Request-ID"]) > 0
