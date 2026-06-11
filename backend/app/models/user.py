from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Utilisateur de l'application EnSoi."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    hashed_password: str = Field(max_length=255, nullable=False)
    nom: str = Field(max_length=100, nullable=False)
    date_naissance: date = Field(nullable=False)
    is_active: bool = Field(default=True)
    refresh_token: Optional[str] = Field(default=None)  # Hashé SHA-256
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
