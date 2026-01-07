import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure required secrets exist for tests
os.environ.setdefault("FERNET_KEY", "gKm2GbnYl8aA0svBLmvBxxtBBAsoAhH2E_n0ilKAIIs=")
os.environ.setdefault("JWT_SECRET", "testsecret")
os.environ.setdefault("POSTGRES_USER", "user")
os.environ.setdefault("POSTGRES_PASSWORD", "pass")
os.environ.setdefault("POSTGRES_DB", "db")
os.environ.setdefault("POSTGRES_HOST", "localhost")

sys.path.append("src")

from app.db.session import Base  # noqa


@pytest.fixture(scope="session")
def in_memory_db():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    yield TestingSessionLocal
    engine.dispose()


@pytest.fixture
def db_session(in_memory_db) -> Session:
    db = in_memory_db()
    try:
        yield db
    finally:
        db.close()

