"""
Router Users - /users/*
Tous les endpoints sont protégés par Bearer token (get_current_user).
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from app.database import get_db as get_session
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.auth import verify_password

router = APIRouter(prefix="/users", tags=["users"])



# Schémas locaux


class UserUpdate(BaseModel):
    """PATCH /users/me - nom et/ou date de naissance (tous optionnels)."""
    nom: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-ZÀ-ÿ\s\-]+$",
    )
    date_naissance: date | None = None


class EmailUpdate(BaseModel):
    """PATCH /users/me/email - nouvel email + MDP pour confirmation."""
    email: EmailStr
    password: str


class DeleteAccount(BaseModel):
    """DELETE /users/me - MDP obligatoire pour confirmer la suppression."""
    password: str


class UserResponse(BaseModel):
    """Réponse standard pour les infos utilisateur."""
    id: int
    nom: str
    email: str
    date_naissance: date

    model_config = {
        "from_attributes": True  # Permet de retourner directement l'objet SQLModel User
    }



# GET /users/me


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Récupérer les infos du compte connecté",
)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Retourne les informations du compte de l'utilisateur connecté.
    Aucune requête BDD supplémentaire - get_current_user a déjà chargé le user.
    """
    return current_user



# PATCH /users/me


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Modifier nom et/ou date de naissance",
)
def update_me(
    body: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """
    Mise à jour partielle - seuls les champs fournis dans le body sont modifiés.
    model_dump(exclude_unset=True) détecte exactement ce que le client a envoyé.
    """
    update_data = body.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Au moins un champ à modifier doit être fourni (nom ou date_naissance).",
        )

    if "nom" in update_data and body.nom:
        current_user.nom = body.nom.strip()

    if "date_naissance" in update_data:
        current_user.date_naissance = body.date_naissance

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user



# PATCH /users/me/email


@router.patch(
    "/me/email",
    response_model=UserResponse,
    summary="Modifier l'email (confirmation MDP requise)",
)
def update_email(
    body: EmailUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """
    Modification de l'email avec confirmation par mot de passe.

    - Vérifie le MDP avant tout changement (action sensible).
    - Vérifie que le nouvel email n'est pas déjà utilisé (409).
    - Normalise l'email en lowercase + strip.
    """
    # 1. Vérifier le MDP
    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect.",
        )

    # 2. Vérifier l'unicité du nouvel email
    new_email = body.email.lower().strip()
    if new_email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouvel email est identique à l'email actuel.",
        )

    existing = session.exec(
        select(User).where(User.email == new_email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email.",
        )

    # 3. Mettre à jour
    current_user.email = new_email
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user



# DELETE /users/me


@router.delete(
    "/me",
    summary="Supprimer le compte (irréversible, cascade sur les profils)",
)
def delete_me(
    body: DeleteAccount,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """
    Suppression définitive du compte utilisateur.

    - Vérifie le MDP avant suppression (action irréversible).
    - ON DELETE CASCADE supprime automatiquement profils et share_tokens.
    """
    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect.",
        )

    session.delete(current_user)
    session.commit()

    return {"message": "Compte supprimé avec succès."}
