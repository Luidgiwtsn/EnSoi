"""
Référentiel de données statiques pour les champs Human Design optionnels.

Expose des fonctions qui retournent les listes de pays et de fuseaux
horaires utilisées par le frontend pour peupler les <select> du formulaire
de génération de profil.

Les listes sont calculées une seule fois au chargement du module (cache
mémoire) puisqu'elles sont totalement statiques sur la durée de vie d'une
instance FastAPI.
"""

import pycountry
from babel import Locale


def _build_countries_list() -> list[dict]:
    """
    Construit la liste des pays au format [{"code": "FR", "name": "France"}, ...].

    Les noms sont en français via Babel. La liste est triée par nom (français)
    pour faciliter l'affichage dans un <select>.

    Cohérent avec la validation backend : le code alpha-2 (ex. "FR") est
    accepté par pycountry côté validation du ProfilRequest.
    """
    locale = Locale("fr")
    pays = []
    for country in pycountry.countries:
        code = country.alpha_2
        # Babel ne traduit que les territoires connus ; fallback sur le nom anglais
        nom = locale.territories.get(code, country.name)
        pays.append({"code": code, "name": nom})

    # Tri alphabétique par nom français (locale-aware grâce au tri standard Python
    # qui gère correctement l'unicode)
    pays.sort(key=lambda p: p["name"])
    return pays


# Cache mémoire : calculé une fois à l'import du module.
COUNTRIES: list[dict] = _build_countries_list()
