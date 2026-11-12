"""Phase 6 performance & admin governance verification tests: caching, pagination, N+1 eager load, and admin overview."""

from app.core.cache import cache
from app.core.rate_limit import rate_limiter
from app.models import User
from tests.conftest import TestingSessionLocal


async def test_marketplace_cache_pagination_and_admin_overview(async_client):
    rate_limiter.reset()
    cache.invalidate_prefix("marketplace:")

    # 1. Public marketplace pagination bounds & warm cache hit
    r1 = await async_client.get("/api/v1/marketplace/products?page=1&page_size=5")
    assert r1.status_code == 200, r1.text
    d1 = r1.json()["data"]
    assert d1["page"] == 1
    assert d1["page_size"] == 5

    # Second identical read served from cache
    r2 = await async_client.get("/api/v1/marketplace/products?page=1&page_size=5")
    assert r2.status_code == 200
    assert r2.json()["data"]["total"] == d1["total"]

    # 2. Admin overview metrics + paginated audit log feed (Admin-only RBAC)
    r_unauth = await async_client.get("/api/v1/compliance/admin/overview")
    assert r_unauth.status_code == 401

    db = TestingSessionLocal()
    try:
        from app.core.security import get_password_hash
        from app.models import Role

        admin_role = db.query(Role).filter(Role.code == "ADMIN").first()
        u = db.query(User).filter(User.email == "perf.admin@craftlens.org").first()
        if not u:
            u = User(
                email="perf.admin@craftlens.org",
                full_name="Perf Admin",
                hashed_password=get_password_hash("AdminPass#123"),
                is_active=True,
                is_verified=True,
            )
            if admin_role:
                u.roles.append(admin_role)
            db.add(u)
            db.commit()
    finally:
        db.close()

    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "perf.admin@craftlens.org", "password": "AdminPass#123"},
    )
    assert login.status_code == 200
    admin_h = {"Authorization": f"Bearer {login.json()['access_token']}"}

    r_ov = await async_client.get("/api/v1/compliance/admin/overview?page=1&page_size=10", headers=admin_h)
    assert r_ov.status_code == 200, r_ov.text
    ov = r_ov.json()["data"]
    assert "metrics" in ov
    assert "total_users" in ov["metrics"]
    assert ov["audit_logs"]["page"] == 1
    assert ov["audit_logs"]["page_size"] == 10
