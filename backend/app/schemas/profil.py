from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError


class ProfilRequest(BaseModel):
    """Données brutes envoyées par le frontend."""
    prenom: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-ZÀ-ÿ \-]+$')
    nom_famille: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-ZÀ-ÿ \-]+$')
    date_naissance: date
    heure_naissance: Optional[time] = None
    pays_naissance: Optional[str] = Field(default=None, max_length=100)
    fuseau_horaire_naissance: Optional[str] = Field(default=None, max_length=50)
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
        if v > date.today():
            raise PydanticCustomError(
                "future_date",
                "La date de naissance ne peut pas être dans le futur"
            )
        return v

    @field_validator('pays_naissance')
    @classmethod
    def valider_pays(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import pycountry
        pays = pycountry.countries.get(name=v) or pycountry.countries.get(alpha_2=v.upper())
        if pays is None:
            raise PydanticCustomError(
                "pays_invalide",
                "Le pays fourni n'est pas reconnu"
            )
        return v

    @field_validator('fuseau_horaire_naissance')
    @classmethod
    def valider_fuseau(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import pytz
        if v not in pytz.all_timezones:
            raise PydanticCustomError(
                "fuseau_invalide",
                "Le fuseau horaire fourni n'est pas reconnu"
            )
        return v


class DimensionCognitive(BaseModel):
    dominant: str
    lettre: str = Field(max_length=1)
    score_pourcentage: int = Field(ge=51, le=100)


class DimensionsCognitives(BaseModel):
    energie: DimensionCognitive
    perception: DimensionCognitive
    decision: DimensionCognitive
    organisation: DimensionCognitive


class ProfilCognitifResult(BaseModel):
    type_cognitif: str = Field(min_length=4, max_length=4)
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
    model_config = ConfigDict(from_attributes=True)

    id: int
    prenom: str
    nom_famille: str
    date_naissance: date
    heure_naissance: Optional[time] = None
    pays_naissance: Optional[str] = None
    fuseau_horaire_naissance: Optional[str] = None
    numerologie: NumerologieResult
    profil_cognitif: ProfilCognitifResult
    human_design: HumanDesignResult
    synthese_ia: Optional[str] = None
    statut: str
    created_at: datetime
