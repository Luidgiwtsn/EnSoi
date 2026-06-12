"""Router profils — POST /api/generate et GET /api/profils."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional

from app.database import get_db
from app.models.profil import Profil
from app.schemas.profil import ProfilRequest, ProfilComplet
from app.services import numerologie, human_design, profil_cognitif

router = APIRouter(prefix="/api", tags=["profils"])


@router.post("/generate", response_model=ProfilComplet)
def generate_profil(
    request: ProfilRequest,
    session: Session = Depends(get_db),
):
    """
    Génère un profil complet à partir des données utilisateur.
    Orchestre les 3 services métier et persiste le résultat en base.
    """
    # 1. Calculer les 3 services
    result_numerologie = numerologie.calculer(
        request.prenom,
        request.nom_famille,
        request.date_naissance,
    )
    result_human_design = human_design.calculer(
        request.date_naissance,
        request.heure_naissance,
        request.lieu_naissance,
    )
    result_cognitif = profil_cognitif.calculer(request.reponses_cognitif)

    # 2. Créer le profil en base (statut pending)
    profil = Profil(
        prenom=request.prenom,
        nom_famille=request.nom_famille,
        date_naissance=request.date_naissance,
        heure_naissance=request.heure_naissance,
        lieu_naissance=request.lieu_naissance,
        numerologie=result_numerologie,
        human_design=result_human_design,
        profil_cognitif=result_cognitif,
        statut="pending",
    )
    session.add(profil)
    session.commit()
    session.refresh(profil)

    # 3. Synthèse IA Groq (à implémenter — pour l'instant statut complet)
    profil.statut = "complet"
    session.add(profil)
    session.commit()
    session.refresh(profil)

    return profil
