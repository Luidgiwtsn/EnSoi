from datetime import date, datetime, time
from typing import Any, Dict, Optional
from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class Profil(SQLModel, table=True):
    """Profil personnalisé généré pour un utilisateur."""

    __tablename__ = "profils"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        ondelete="CASCADE",   # Suppression compte → suppression profils
        index=True,
    )
    prenom: str = Field(max_length=100, nullable=False)
    nom_famille: str = Field(max_length=100, nullable=False)
    date_naissance: date = Field(nullable=False)
    heure_naissance: Optional[time] = Field(default=None, nullable=True)
    pays_naissance: Optional[str] = Field(default=None, max_length=100, nullable=True)
    fuseau_horaire_naissance: Optional[str] = Field(default=None, max_length=50, nullable=True)

    # Résultats algorithmiques — JSONB flexible
    numerologie: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    profil_cognitif: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    human_design: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))

    synthese_ia: Optional[str] = Field(default=None)  # None si Groq indisponible
    statut: str = Field(default="pending", max_length=20)  # pending|complet|partiel
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
