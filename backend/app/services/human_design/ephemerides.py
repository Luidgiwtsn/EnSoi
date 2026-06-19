# backend/app/services/human_design/ephemerides.py
"""
Calcul des positions planétaires via pyswisseph (Swiss Ephemeris).

Ce module convertit une date/heure/lieu en positions zodiacales
(en degrés, 0-360) pour les 13 points utilisés en Human Design :
les 9 planètes classiques + la Terre (toujours opposée au Soleil)
+ le Nœud Nord et Nœud Sud de la Lune + Pluton.

CORRECTION (juin 2026) : la version précédente ne calculait que 9 corps
célestes et omettait la Terre, les Nœuds Lunaires et Pluton — ce qui
faussait silencieusement le calcul des canaux et centres en aval (gates
manquantes, canaux non détectés). Voir le test d'intégration sur la
charte de référence Henry Dupont qui a révélé ce manque (canal 37-40
non détecté faute des bons points actifs).

Aucune autre logique Human Design ici — juste de l'astronomie.
"""
import swisseph as swe
from datetime import datetime, date, time
from typing import Dict
import pytz


# Les 9 planètes classiques, avec leur constante pyswisseph
PLANETES = {
    "soleil": swe.SUN,
    "lune": swe.MOON,
    "mercure": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturne": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluton": swe.PLUTO,
}


CODE_NOEUD_NORD = swe.TRUE_NODE


def _vers_julian_day_utc(
    date_naissance: date,
    heure_naissance: time,
    fuseau_horaire: str,
) -> float:
    """
    Convertit une date/heure locale + fuseau horaire en Julian Day UTC.
    """
    dt_naive = datetime.combine(date_naissance, heure_naissance)
    tz = pytz.timezone(fuseau_horaire)
    dt_localise = tz.localize(dt_naive)
    dt_utc = dt_localise.astimezone(pytz.utc)

    heure_decimale = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600

    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        heure_decimale,
    )


def calculer_positions_planetaires(jour_julien: float) -> Dict[str, float]:
    """
    Calcule la position zodiacale (0-360°) de chaque point utilisé en
    Human Design à un Julian Day donné : 9 planètes classiques + Terre
    + Nœud Nord + Nœud Sud + Pluton (13 points au total).

    La Terre n'est pas calculée via swe.calc_ut (ce serait la position
    du Soleil vu depuis la Terre elle-même, ce qui n'a pas de sens) —
    elle est déduite du Soleil par opposition exacte (+180°), comme le
    fait toute implémentation Human Design standard.

    Le Nœud Sud est déduit du Nœud Nord par opposition exacte (+180°).

    Retourne un dict {nom_point: degre_zodiacal}.
    """
    positions = {}
    flag = swe.FLG_MOSEPH | swe.FLG_SPEED

    for nom, code_planete in PLANETES.items():
        resultat, _ = swe.calc_ut(jour_julien, code_planete, flag)
        positions[nom] = resultat[0]

    # Terre : toujours exactement opposee au Soleil
    positions["terre"] = (positions["soleil"] + 180) % 360

    # Noeud Nord (Mean Node) et Noeud Sud (oppose exact)
    resultat_noeud, _ = swe.calc_ut(jour_julien, CODE_NOEUD_NORD, flag)
    positions["noeud_nord"] = resultat_noeud[0]
    positions["noeud_sud"] = (resultat_noeud[0] + 180) % 360

    return positions


def _trouver_jour_julien_88_jours_avant(jour_julien_naissance: float) -> float:
    """
    Trouve le Julian Day où le Soleil était exactement à 88° de moins
    que sa position de naissance (le "point de design" en Human Design).
    """
    flag = swe.FLG_MOSEPH | swe.FLG_SPEED

    soleil_naissance, _ = swe.calc_ut(jour_julien_naissance, swe.SUN, flag)
    degre_cible = (soleil_naissance[0] - 88) % 360

    jour_julien_estime = jour_julien_naissance - 88.5

    for _ in range(10):
        soleil_estime, _ = swe.calc_ut(jour_julien_estime, swe.SUN, flag)
        degre_actuel = soleil_estime[0]

        ecart = (degre_cible - degre_actuel + 180) % 360 - 180

        if abs(ecart) < 0.0001:
            break

        vitesse_solaire = soleil_estime[3] if len(soleil_estime) > 3 else 0.9856
        jour_julien_estime += ecart / vitesse_solaire

    return jour_julien_estime


def calculer_double_carte(
    date_naissance: date,
    heure_naissance: time,
    fuseau_horaire: str,
) -> Dict[str, Dict[str, float]]:
    """
    Point d'entrée principal du module.

    Calcule les deux cartes nécessaires au Human Design :
    - "conscient" : positions au moment exact de la naissance (13 points)
    - "inconscient" : positions 88° solaires avant la naissance (13 points)
    """
    jour_julien_naissance = _vers_julian_day_utc(
        date_naissance, heure_naissance, fuseau_horaire
    )
    jour_julien_design = _trouver_jour_julien_88_jours_avant(jour_julien_naissance)

    return {
        "conscient": calculer_positions_planetaires(jour_julien_naissance),
        "inconscient": calculer_positions_planetaires(jour_julien_design),
    }
