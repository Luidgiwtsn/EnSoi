"""Connexion PostgreSQL via SQLModel."""

from sqlmodel import SQLModel, Session, create_engine
from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=not settings.is_production(),
    pool_pre_ping=True,
)


def create_db_and_tables() -> None:
    """Crée les tables (développement uniquement)."""
    SQLModel.metadata.create_all(engine)


def get_db():
    """Dépendance FastAPI — session BDD par requête."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
