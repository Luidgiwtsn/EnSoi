# app/routers/profils.py
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select

from app.database import get_db
from app.models.profil import Profil
from app.models.share_token import ShareToken
from app.models.user import User
from app.routers.auth import get_current_user, get_current_user_optional
from app.schemas.profil import ProfilRequest, ProfilComplet
from app.services.numerologie import calculer as calculer_numerologie
from app.services.human_design import calculer as calculer_human_design
from app.services.profil_cognitif import (
    calculer as calculer_profil_cognitif,
    get_questions as get_questions_cognitif,
)
from app.services.groq_service import GroqService
from app.rate_limiter import limiter
from app.config import get_settings

router = APIRouter()
public_router = APIRouter()  # routes exposées sans préfixe /api (lien de partage)
settings = get_settings()


# GET /api/cognitif/questions  - liste des 12 questions du questionnaire

@router.get("/cognitif/questions")
def list_questions_cognitif():
    """
    Retourne la liste des 12 questions du questionnaire cognitif.
    Endpoint public (pas d'authentification requise) - appelé par le frontend
    au démarrage du questionnaire.

    Source unique de vérité : les questions sont définies dans la constante
    QUESTIONS de app/services/profil_cognitif.py. Toute modification se fait
    dans ce service, le frontend récupère automatiquement la nouvelle version.

    Chaque question contient :
    - id (int) : numéro 1..12
    - axe (str) : energie | perception | decision | organisation
    - texte (str) : énoncé de la question
    - pole_a (str) : énoncé du pôle à gauche du curseur (réponse 1)
    - pole_b (str) : énoncé du pôle à droite du curseur (réponse 5)
    """
    return {"questions": get_questions_cognitif()}

# POST /api/generate


@router.post("/generate", response_model=ProfilComplet, status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def generate_profil(
    request: Request,
    payload: ProfilRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Génère un profil complet à partir des données personnelles et du questionnaire
    cognitif. L'utilisateur peut être connecté (user_id associé) ou anonyme.
    Retourne toujours 200, avec statut='partiel' si Groq est indisponible.
    """
    # 1. Calculs des trois services métier
    numerologie = calculer_numerologie(
        payload.prenom, payload.nom_famille, payload.date_naissance
    )
    human_design = calculer_human_design(
        payload.date_naissance,
        payload.heure_naissance,
        payload.pays_naissance,
        payload.fuseau_horaire_naissance,
    )
    profil_cognitif = calculer_profil_cognitif(payload.reponses_cognitif)

    # 2. Insertion en BDD avec statut pending
    # db.refresh après le premier commit garantit que profil.id est renseigné
    # avant l'appel Groq, même si SQLModel invalide l'objet en mémoire.
    # claim_token : UUID one-shot genere uniquement pour les profils anonymes.
    # Permet a un utilisateur de rattacher ce profil a son compte apres inscription.
    # Pour un utilisateur deja connecte, le profil est immediatement rattache (user_id set)
    claim_token = str(uuid.uuid4()) if current_user is None else None

    profil = Profil(
        user_id=current_user.id if current_user else None,
        prenom=payload.prenom,
        nom_famille=payload.nom_famille,
        date_naissance=payload.date_naissance,
        heure_naissance=payload.heure_naissance,
        pays_naissance=payload.pays_naissance,
        fuseau_horaire_naissance=payload.fuseau_horaire_naissance,
        numerologie=numerologie,
        profil_cognitif=profil_cognitif,
        human_design=human_design,
        synthese_ia=None,
        statut="pending",
        claim_token=claim_token,
    )
    db.add(profil)
    db.commit()
    db.refresh(profil)  # garantit profil.id disponible avant appel Groq

    # 3. Synthèse IA via Groq (timeout 8s, circuit breaker)
    # Le service retourne None si Groq est indisponible (circuit breaker
    # ou timeout) — pas une exception. statut='partiel' dans ce cas.
    groq_service = GroqService()
    profil_data = {
        "prenom": payload.prenom,
        "nom_famille": payload.nom_famille,
        "date_naissance": payload.date_naissance.isoformat(),
        "numerologie": numerologie,
        "human_design": human_design,
        "profil_cognitif": profil_cognitif,
    }
    synthese_ia = groq_service.generer_synthese(profil_data)
    if synthese_ia is not None:
        profil.synthese_ia = synthese_ia
        profil.statut = "complet"
    else:
        profil.statut = "partiel"

    db.add(profil)
    db.commit()
    db.refresh(profil)

    return profil



# GET /api/profils  - historique de l'utilisateur connecté


@router.get("/profils", response_model=list[ProfilComplet])
def list_profils(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retourne la liste des profils appartenant à l'utilisateur connecté,
    triée du plus récent au plus ancien.
    Filtre obligatoire par user_id (protection IDOR).
    """
    statement = (
        select(Profil)
        .where(Profil.user_id == current_user.id)
        .order_by(Profil.created_at.desc())
    )
    profils = db.exec(statement).all()
    return profils



# GET /api/profils/{id}  - accès public au profil (si owner ou anonyme OK)


@router.get("/profils/{profil_id}", response_model=ProfilComplet)
def get_profil(
    profil_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Retourne un profil par son ID.
    - Si le profil a un user_id : seul le propriétaire peut y accéder (403 sinon).
    - Si user_id est NULL (profil anonyme) : accessible sans auth.
    """
    profil = db.get(Profil, profil_id)
    if not profil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil introuvable")

    if profil.user_id is not None:
        if current_user is None or profil.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    return profil



# DELETE /api/profils/{id}


@router.delete("/profils/{profil_id}", status_code=status.HTTP_200_OK)
def delete_profil(
    profil_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Supprime un profil. Seul le propriétaire peut supprimer son profil.
    Les share_tokens associés sont supprimés en cascade (ON DELETE CASCADE).
    """
    profil = db.get(Profil, profil_id)
    if not profil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil introuvable")

    if profil.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    db.delete(profil)
    db.commit()
    return {"message": "Profil supprimé"}



# POST /api/profils/{id}/share


@router.post("/profils/{profil_id}/share", status_code=status.HTTP_201_CREATED)
def share_profil(
    profil_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Génère un lien de partage public valable 30 jours pour un profil.
    Seul le propriétaire peut créer un lien de partage.
    Si un token actif existe déjà pour ce profil, retourne le token existant
    (évite la prolifération de tokens).

    Note timezone : on utilise un datetime sans tzinfo (naive UTC) pour la
    comparaison avec expires_at en BDD, qui est stocké sans fuseau horaire
    par PostgreSQL/SQLite. Cela évite le TypeError offset-naive vs offset-aware.
    """
    profil = db.get(Profil, profil_id)
    if not profil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil introuvable")

    if profil.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    # datetime naive UTC : compatible avec le stockage PostgreSQL/SQLite sans tzinfo
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)

    existing = db.exec(
        select(ShareToken)
        .where(ShareToken.profil_id == profil_id)
        .where(ShareToken.is_active == True)  # noqa: E712
        .where(ShareToken.expires_at > now_naive)
    ).first()

    if existing:
        token_str = existing.token
        expires_at = existing.expires_at
    else:
        token_str = secrets.token_urlsafe(32)
        expires_at = now_naive + timedelta(days=30)

        share_token = ShareToken(
            profil_id=profil_id,
            token=token_str,
            expires_at=expires_at,
            is_active=True,
        )
        db.add(share_token)
        db.commit()
        db.refresh(share_token)

    base_url = settings.FRONTEND_URL
    return {
        "url": f"{base_url}/public/{token_str}",
        "token": token_str,
        "expires_at": expires_at.isoformat(),
    }



# GET /public/{token} - accès public sans authentification


@public_router.get("/public/{token}", response_model=ProfilComplet)
def get_profil_public(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Retourne un profil via son token de partage.
    Vérifie que le token existe, est actif et n'est pas expiré.

    Note timezone : même logique que share_profil — datetime naive UTC
    pour éviter le TypeError lors de la comparaison avec expires_at en BDD.
    """
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)

    share_token = db.exec(
        select(ShareToken)
        .where(ShareToken.token == token)
        .where(ShareToken.is_active == True)  # noqa: E712
        .where(ShareToken.expires_at > now_naive)
    ).first()

    if not share_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lien de partage invalide ou expiré",
        )

    profil = db.get(Profil, share_token.profil_id)
    if not profil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil introuvable")

    return profil
