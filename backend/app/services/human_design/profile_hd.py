# backend/app/services/human_design/profile_hd.py
#
# Renommé en profile_hd.py (et non profile.py) pour éviter le conflit
# avec le module standard Python `profile` (profileur de performance).
"""
Calcul du Profil Human Design.

Le Profil est noté X/Y où :
- X = ligne du Soleil conscient (Personnalité), de 1 à 6
- Y = ligne du Soleil inconscient (Design), de 1 à 6

Seules 12 combinaisons existent parmi les 36 mathématiquement possibles
(6 × 6) - c'est une particularité de la géométrie de la roue Rave.

VALIDATION EMPIRIQUE EFFECTUEE (juin 2026) :
Liste des 12 profils confirmée par 5+ sources indépendantes :
- humdes.com/kb/profiles/
- humandesignsystem.co
- jamielpalmer.com
- yourtango.com
- soul-flow.app

Aucune divergence entre les sources.

Les 6 lignes ont leurs archétypes nommés (Investigateur, Ermite, Martyr,
Opportuniste, Hérétique, Modèle) en français.

Cas de référence Henry Dupont :
- Soleil conscient en Gate 38 Ligne 2
- Soleil inconscient en Gate 48 Ligne 4
- Profil attendu : 2/4 (Hermit / Opportunist = Ermite / Opportuniste)
- Charte officielle Jovian Archive : "Profil 2/4 - Hermit / Opportunist" ✓
"""
from typing import Dict


# Nom français de chaque ligne (de 1 à 6)
LIGNES = {
    1: "Investigateur",
    2: "Ermite",
    3: "Martyr",
    4: "Opportuniste",
    5: "Hérétique",
    6: "Modèle",
}

# Les 12 profils valides en Human Design
PROFILS_VALIDES = {
    (1, 3): "Investigateur / Martyr",
    (1, 4): "Investigateur / Opportuniste",
    (2, 4): "Ermite / Opportuniste",
    (2, 5): "Ermite / Hérétique",
    (3, 5): "Martyr / Hérétique",
    (3, 6): "Martyr / Modèle",
    (4, 6): "Opportuniste / Modèle",
    (4, 1): "Opportuniste / Investigateur",
    (5, 1): "Hérétique / Investigateur",
    (5, 2): "Hérétique / Ermite",
    (6, 2): "Modèle / Ermite",
    (6, 3): "Modèle / Martyr",
}

assert len(PROFILS_VALIDES) == 12, "Il doit y avoir exactement 12 profils valides"


def determiner_profil(ligne_soleil_conscient: int, ligne_soleil_inconscient: int) -> Dict[str, str]:
    """
    Calcule le profil Human Design à partir des lignes du Soleil conscient
    et du Soleil inconscient.

    Retourne un dict :
    - notation : str (ex: "2/4")
    - nom : str (ex: "Ermite / Opportuniste")
    - valide : bool (True si la combinaison fait partie des 12 profils
      standards, False si elle est mathématiquement possible mais hors
      des 12 profils valides — peut indiquer une erreur de calcul amont)

    En théorie, vu la géométrie de la roue Rave, seules les 12 combinaisons
    listées dans PROFILS_VALIDES devraient apparaître. Si une autre
    combinaison sort, c'est probablement le signe d'un bug dans le calcul
    des positions astronomiques ou de l'offset.
    """
    cle = (ligne_soleil_conscient, ligne_soleil_inconscient)
    notation = f"{ligne_soleil_conscient}/{ligne_soleil_inconscient}"

    if cle in PROFILS_VALIDES:
        return {
            "notation": notation,
            "nom": PROFILS_VALIDES[cle],
            "valide": True,
        }

    # Combinaison hors des 12 profils valides - on retourne tout de même
    # une notation lisible, mais on marque le profil comme non standard.
    nom_l1 = LIGNES.get(ligne_soleil_conscient, "?")
    nom_l2 = LIGNES.get(ligne_soleil_inconscient, "?")
    return {
        "notation": notation,
        "nom": f"{nom_l1} / {nom_l2} (combinaison non standard)",
        "valide": False,
    }
