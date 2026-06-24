"""
Endpoints de référence pour peupler les listes déroulantes du frontend.

Données statiques (pays, fuseaux horaires) servies depuis le cache mémoire.
Endpoints publics — pas d'auth, pas de rate limit.
"""

from fastapi import APIRouter

from app.services.reference_data import COUNTRIES

router = APIRouter(prefix="/api", tags=["reference"])


@router.get("/countries")
def list_countries() -> dict:
    """
    Retourne la liste des pays avec leur code alpha-2 et leur nom français.

    Format : {"countries": [{"code": "FR", "name": "France"}, ...]}

    Trié par nom alphabétique. Cohérent avec la validation pycountry du
    backend qui accepte le code alpha-2 (ex. "FR") sur le champ
    `pays_naissance` de POST /api/generate.
    """
    return {"countries": COUNTRIES}
