"""Router profils — /api/generate, /api/profils, /api/health."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_db
from app.models.profil import Profil
from app.schemas.profil import ProfilComplet, ProfilRequest
from app.services import human_design, numerologie, profil_cognitif
from app.services.groq_service import get_groq_service

router = APIRouter(prefix="/api", tags=["profils"])


@router.get("/health")
def health_check(session: Session = Depends(get_db)):
    """Vérifie que l'API et la base de données sont opérationnelles."""
    try:
        session.exec(select(Profil).limit(1))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "version": "1.0.0", "database": db_status}


@router.post("/generate", response_model=ProfilComplet, status_code=status.HTTP_201_CREATED)
def generate_profil(
    request: ProfilRequest,
    session: Session = Depends(get_db),
):
    """
    Génère un profil complet à partir des données utilisateur.
    Orchestre les 3 services métier + synthèse Groq et persiste en base.
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

    # 2. Persister en base (statut pending)
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

    # 3. Synthèse Groq — retourne None si indisponible
    profil_data = {
        "prenom": profil.prenom,
        "nom_famille": profil.nom_famille,
        "date_naissance": str(profil.date_naissance),
        "numerologie": profil.numerologie,
        "human_design": profil.human_design,
        "profil_cognitif": profil.profil_cognitif,
    }
    synthese = get_groq_service().generer_synthese(profil_data)

    profil.synthese_ia = synthese
    profil.statut = "complet" if synthese else "partiel"
    session.add(profil)
    session.commit()
    session.refresh(profil)

    return profil


@router.get("/profils", response_model=List[ProfilComplet])
def list_profils(session: Session = Depends(get_db)):
    """Retourne tous les profils (auth à brancher en feature/auth-jwt)."""
    profils = session.exec(select(Profil).order_by(Profil.created_at.desc())).all()
    return profils


@router.get("/profils/{profil_id}", response_model=ProfilComplet)
def get_profil(profil_id: int, session: Session = Depends(get_db)):
    """Retourne un profil par son ID."""
    profil = session.get(Profil, profil_id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil introuvable")
    return profil


@router.delete("/profils/{profil_id}", status_code=status.HTTP_200_OK)
def delete_profil(profil_id: int, session: Session = Depends(get_db)):
    """Supprime un profil (ownership vérifié en feature/auth-jwt)."""
    profil = session.get(Profil, profil_id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil introuvable")
    session.delete(profil)
    session.commit()
    return {"message": "Profil supprimé"}
