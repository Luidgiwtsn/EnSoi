from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ShareToken(SQLModel, table=True):
    """Token de partage public d'un profil (durée 30 jours)."""

    __tablename__ = "share_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    profil_id: int = Field(foreign_key="profils.id", nullable=False, index=True)
    token: str = Field(max_length=64, unique=True, nullable=False, index=True)
    expires_at: datetime = Field(nullable=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
