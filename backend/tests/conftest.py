"""Fixtures pytest partagées."""

import pytest
from app.rate_limiter import limiter

# Désactivation globale du rate limiting pour la suite de tests existants.
# Les tests spécifiques au rate limiting (test_rate_limiting.py) le réactivent
# explicitement via un fixture pour leurs assertions.
limiter.enabled = False
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_db


@pytest.fixture(name="client")
def client_fixture():
    """Client HTTP avec BDD SQLite en mémoire."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_db_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = get_db_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
