from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError


class ProfilRequest(BaseModel):
    """Données brutes envoyées par le frontend."""

    prenom: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-ZÀ-ÿ\s\-]+$')
    nom_famille: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-ZÀ-ÿ\s\-]+$')
    date_naissance: date
    heure_naissance: Optional[time] = None
    lieu_naissance: Optional[str] = Field(default=None, max_length=200)
    reponses_cognitif: List[int] = Field(min_length=12, max_length=12)

    @field_validator('reponses_cognitif')
    @classmethod
    def valider_reponses(cls, v: List[int]) -> List[int]:
        if not all(1 <= r <= 5 for r in v):
            raise PydanticCustomError(
                "score_out_of_range",
                "Chaque réponse doit être un entier compris entre 1 et 5"
            )
        return v

    @field_validator('date_naissance')
    @classmethod
    def valider_date(cls, v: date) -> date:
        # Évaluation dynamique de la date du jour à la seconde de l'appel
        if v > date.today():
            raise PydanticCustomError(
                "future_date",
                "La date de naissance ne peut pas être dans le futur"
            )
        return v


class DimensionCognitive(BaseModel):
    dominant: str
    lettre: str = Field(max_length=1)  # Contrainte pour forcer 'I', 'E', 'N', etc.
    score_pourcentage: int = Field(ge=51, le=100)  # Un score dominant fait minimum 51% suite à notre optimisation


class DimensionsCognitives(BaseModel):
    energie: DimensionCognitive
    perception: DimensionCognitive
    decision: DimensionCognitive
    organisation: DimensionCognitive


class ProfilCognitifResult(BaseModel):
    type_cognitif: str = Field(min_length=4, max_length=4)  # Ex: INFJ
    nom_profil: str
    dimensions: DimensionsCognitives


class NumerologieResult(BaseModel):
    chemin_vie: int = Field(ge=1, le=33)
    expression: int = Field(ge=1, le=33)
    intime: int = Field(ge=1, le=33)
    realisation: int = Field(ge=1, le=33)


class HumanDesignResult(BaseModel):
    type_hd: str
    strategie: str
    profil: str
    autorite: str
    donnees_completes: bool


class ProfilComplet(BaseModel):
    """Réponse complète retournée au frontend."""
    
    # Syntaxe moderne Pydantic V2 pour la configuration globale
    model_config = ConfigDict(from_attributes=True)

    id: int
    prenom: str
    nom_famille: str
    date_naissance: date
    heure_naissance: Optional[time] = None
    lieu_naissance: Optional[str] = None
    numerologie: NumerologieResult
    profil_cognitif: ProfilCognitifResult
    human_design: HumanDesignResult
    synthese_ia: Optional[str] = None
    statut: str
