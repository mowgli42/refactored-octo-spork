import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import shutil
from unittest.mock import MagicMock

from backend.database import Base
from backend import main
from backend.main import app, get_db

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for a test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a new TestClient that uses the test database."""
    
    # Override the dependency for routes
    def override_get_db():
        try:
            yield db_session
        finally:
            pass # Don't close here, let fixture handle it

    app.dependency_overrides[get_db] = override_get_db
    
    # Patch the SessionLocal used by background tasks to return our test session
    # Note: Background tasks run in a thread, but with StaticPool and check_same_thread=False,
    # it should work if they use the same engine.
    # However, since BackgroundTasks run AFTER the response, we need to ensure 
    # the session is valid. 
    # For simplicity in this test setup, we'll execute the background task synchronously 
    # or rely on the shared engine.
    
    # Crucial: Override the global SessionLocal in main.py so background task uses test DB
    original_session_local = main.SessionLocal
    main.SessionLocal = lambda: db_session 
    
    yield TestClient(app)
    
    # Cleanup
    del app.dependency_overrides[get_db]
    main.SessionLocal = original_session_local

@pytest.fixture(scope="session", autouse=True)
def cleanup_cache():
    """Cleanup cache directory after tests."""
    yield
    if os.path.exists("backend/cache"):
        # Only clean up test-generated files if we were isolating paths, 
        # but for now we share the cache dir. In a real app we'd configure a test cache dir.
        pass
