"""
Router Auth - /auth/*
Endpoints publics (pas de token requis sauf /auth/logout et /auth/change-password).
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_db as get_session
from app.models.user import User
from app.rate_limiter import limiter
from app.schemas.auth import Token, UserCreate, UserLogin, ChangePasswordRequest
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
    decode_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Schéma de sécurité Bearer - active le cadenas dans Swagger UI
security = HTTPBearer()
# Version optionnelle - retourne None si pas de token au lieu de lever 403
security_optional = HTTPBearer(auto_error=False)


class RefreshTokenRequest(BaseModel):
    """Corps attendu par POST /auth/refresh."""
    refresh_token: str



# Helpers & dépendances


def _validate_password_strength(password: str) -> None:
    """
    Règles de complexité : min 8 car., 1 majuscule, 1 chiffre.
    Lève HTTPException 400 si non respectées.
    Mutualisé entre /register et /change-password.
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins 8 caractères.",
        )
    if not any(c.isupper() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins une majuscule.",
        )
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins un chiffre.",
        )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """
    Dépendance FastAPI réutilisable : extrait le Bearer token depuis
    le header HTTP Authorization, valide le JWT et retourne l'utilisateur.

    Injectable via Depends(get_current_user) sur toute route protégée
    (ici /logout et /change-password, et dans routers/users.py).
    Lève 401 si le token est absent, invalide, expiré ou révoqué.
    """
    token = credentials.credentials
    payload = decode_access_token(token)  # lève 401 si invalide/expiré

    user_id: int = int(payload.get("sub"))
    user = session.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable ou inactif.",
        )
    return user

def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_optional)],
    session: Annotated[Session, Depends(get_session)],
) -> Optional[User]:
    """
    Dépendance optionnelle : retourne l'utilisateur si token valide,
    None si pas de token. Utilisée sur les routes accessibles aux anonymes.
    """
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id: int = int(payload.get("sub"))
        user = session.get(User, user_id)
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None


# POST /auth/register


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte utilisateur",
)
def register(
    body: UserCreate,
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    """
    Inscription d'un nouvel utilisateur.

    1. Vérifie l'unicité de l'email (409 si doublon).
    2. Valide la complexité du mot de passe.
    3. Hache le mot de passe avec bcrypt (work factor 12).
    4. Crée l'utilisateur en BDD.
    5. Retourne access_token (30 min) + refresh_token (7 j, stocké hashé sha256).
    """
    # 1. Unicité email - normalisé lowercase + strip avant comparaison et stockage
    existing = session.exec(
        select(User).where(User.email == body.email.lower().strip())
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email.",
        )

    # 2. Complexité MDP
    _validate_password_strength(body.password)

    # 3. Hachage bcrypt
    hashed_pw = hash_password(body.password)

    # 4. Création utilisateur
    user = User(
        email=body.email.lower().strip(),
        hashed_password=hashed_pw,
        prenom=body.prenom.strip(),
        nom_famille=body.nom_famille.strip(),
        date_naissance=body.date_naissance,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # 5. Génération tokens + persistance refresh hashé
    access_token = create_access_token(subject=str(user.id))
    refresh_token_plain = create_refresh_token()

    user.refresh_token = hash_token(refresh_token_plain)
    session.add(user)
    session.commit()

    return Token(access_token=access_token, refresh_token=refresh_token_plain)



# POST /auth/login


@router.post(
    "/login",
    response_model=Token,
    summary="Connexion utilisateur",
)
@limiter.limit("5/minute")
def login(
    request: Request,
    body: UserLogin,
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    """
    Authentification par email + mot de passe.

    Message d'erreur 401 intentionnellement générique pour ne pas révéler
    l'existence d'un compte (protection contre l'user enumeration).
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou mot de passe incorrect.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = session.exec(
        select(User).where(User.email == body.email.lower().strip())
    ).first()
    if not user or not user.is_active:
        raise credentials_error
    if not verify_password(body.password, user.hashed_password):
        raise credentials_error

    access_token = create_access_token(subject=str(user.id))
    refresh_token_plain = create_refresh_token()

    user.refresh_token = hash_token(refresh_token_plain)
    session.add(user)
    session.commit()

    return Token(access_token=access_token, refresh_token=refresh_token_plain)



# POST /auth/refresh


@router.post(
    "/refresh",
    response_model=Token,
    summary="Renouveler les tokens via refresh token",
)
def refresh(
    body: RefreshTokenRequest,
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    """
    Échange un refresh_token valide contre un nouveau couple access/refresh.

    Rotation complète : l'ancien token est invalidé à chaque appel.
    Si un attaquant utilise un token volé avant le propriétaire, la prochaine
    tentative légitime retourne 401 (détection de réutilisation).
    """
    token_hash = hash_token(body.refresh_token)
    user = session.exec(
        select(User).where(User.refresh_token == token_hash)
    ).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou révoqué.",
        )

    new_access = create_access_token(subject=str(user.id))
    new_refresh_plain = create_refresh_token()

    user.refresh_token = hash_token(new_refresh_plain)
    session.add(user)
    session.commit()

    return Token(access_token=new_access, refresh_token=new_refresh_plain)



# POST /auth/logout  (Bearer requis)


@router.post(
    "/logout",
    summary="Déconnexion - invalide le refresh token",
)
def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """
    Invalide le refresh token en BDD.

    L'access token reste valide jusqu'à son expiration (30 min) - comportement
    standard pour les JWT stateless. Retourne 200 même si déjà déconnecté
    (idempotent).
    """
    current_user.refresh_token = None
    session.add(current_user)
    session.commit()
    return {"message": "Déconnexion réussie."}



# POST /auth/change-password  (Bearer requis)


@router.post(
    "/change-password",
    summary="Changer le mot de passe (authentifié)",
)
def change_password(
    body: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """
    Modification du mot de passe pour un utilisateur connecté.

    Vérifie le mot de passe actuel, applique les règles de complexité,
    puis invalide le refresh token pour forcer la reconnexion sur tous
    les appareils.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe actuel incorrect.",
        )

    _validate_password_strength(body.new_password)

    current_user.hashed_password = hash_password(body.new_password)
    current_user.refresh_token = None  # déconnexion globale
    session.add(current_user)
    session.commit()

    return {"message": "Mot de passe modifié avec succès."}
