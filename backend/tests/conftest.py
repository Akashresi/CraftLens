import os

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import get_db
from app.main import app

TEST_DB_FILE = "./test_craftlens.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    init_db(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
async def async_client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()


def create_test_artisan(
    db, email: str, full_name: str, password: str = "ArtisanPass#123", preferred_language: str = "ta"
):
    from app.core.security import get_password_hash
    from app.models import ArtisanProfile, Role, User

    artisan_role = db.query(Role).filter(Role.code == "ARTISAN").first()
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        preferred_language=preferred_language,
        is_active=True,
        is_verified=True,
    )
    if artisan_role:
        user.roles.append(artisan_role)
    db.add(user)
    db.flush()
    profile = ArtisanProfile(
        user_id=user.id,
        craft_specialization="General Traditional Handicrafts",
        city="Varanasi",
        state="Uttar Pradesh",
        experience_years=10,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user
