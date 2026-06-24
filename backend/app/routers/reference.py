"""
Endpoints de référence pour peupler les listes déroulantes du frontend.

Données statiques (pays, fuseaux horaires) servies depuis le cache mémoire.
Endpoints publics — pas d'auth, pas de rate limit.
"""

from fastapi import APIRouter

from app.services.reference_data import COUNTRIES, TIMEZONES

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

@router.get("/timezones")
def list_timezones() -> dict:
    """
    Retourne la liste des fuseaux horaires IANA triée alphabétiquement.

    Format : {"timezones": ["Africa/Abidjan", "Europe/Paris", ...]}

    Cohérent avec pytz.all_timezones utilisé par la validation backend
    du champ fuseau_horaire_naissance du ProfilRequest.
    """
    return {"timezones": TIMEZONES}
