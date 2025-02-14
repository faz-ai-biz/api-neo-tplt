import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.db.models import Base
from src.db.session import get_db
from src.main import app
from tests.utils import create_test_token


@pytest.fixture
def test_db():
    """Create test database and tables"""
    test_engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield TestingSessionLocal
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(test_db):
    """Create test client with database session"""

    def override_get_db():
        try:
            db = test_db()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setattr(settings, "ENVIRONMENT", "test")
    monkeypatch.setattr(settings, "TOKEN_AUDIENCE", "test-audience")
    monkeypatch.setattr(settings, "AUTH_SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(settings, "AUTH_TOKEN_AUDIENCE", "test-audience")
    monkeypatch.setattr(settings, "AUTH_TOKEN_ISSUER", "test-issuer")

    # Filter out Pydantic deprecation warnings
    import warnings

    warnings.filterwarnings(
        "ignore", message="Support for class-based.*", category=DeprecationWarning
    )
    yield


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup test data after each test"""
    yield
    # Cleanup procedures as specified in test plan
    import shutil
    import os

    # 1. Remove test files
    test_files_dir = "/tmp/test_files"
    if os.path.exists(test_files_dir):
        shutil.rmtree(test_files_dir)

    # 2. Clear test directories
    os.makedirs(test_files_dir, exist_ok=True)

    # 3. Remove symlinks (if any)
    test_symlinks_dir = "/tmp/test_symlinks"
    if os.path.exists(test_symlinks_dir):
        shutil.rmtree(test_symlinks_dir)

    # 4. Clear JWT test tokens (if using Redis/cache)
    try:
        from src.core.cache import clear_test_tokens

        clear_test_tokens()
    except ImportError:
        pass  # Module not implemented yet

    # 5. Reset rate limiting counters
    try:
        from src.core.rate_limit import reset_test_counters

        reset_test_counters()
    except ImportError:
        pass  # Module not implemented yet


@pytest.fixture
def valid_token() -> str:
    """Create a valid token with default test scopes"""
    return create_test_token(scopes=["files:read"])


@pytest.fixture
def auth_headers(valid_token) -> dict:
    """Create headers with valid authentication token"""
    return {"Authorization": f"Bearer {valid_token}"}
