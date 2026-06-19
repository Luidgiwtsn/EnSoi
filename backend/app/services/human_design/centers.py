# backend/app/services/human_design/centers.py
"""
Table des 9 centres du Human Design et logique de détermination
des centres définis.

VALIDATION EMPIRIQUE EFFECTUEE (juin 2026) :
- Table des gates par centre confirmée par deux sources indépendantes
  (freehumandesignchart.com et everites.substack.com).
- Vérification structurelle : 64 gates au total, sans doublon, toutes
  présentes (1-64), 0 incohérence avec les 36 canaux validés
  (chaque canal relie bien deux gates de centres différents).
- Cas de référence Henry Dupont : 3 canaux actifs (10-20, 35-36, 37-40)
  → 4 centres définis attendus (G, Throat, Solar Plexus, Heart) →
  cohérent avec la charte officielle Jovian Archive.

Un centre est "défini" si et seulement si au moins un canal qui le
traverse est actif (les deux gates de ce canal allumées). Si aucun
canal ne le traverse, le centre est "ouvert" (open) ou "non défini"
(undefined) selon qu'il a 0 ou >=1 gates actives.
"""
from typing import Dict, List, Set, Tuple
from app.services.human_design.channels import CANAUX


# Les 9 centres du Human Design et leurs gates respectives.
# Total : 64 gates réparties sur 9 centres.
CENTRES: Dict[str, List[int]] = {
    "head":         [61, 63, 64],
    "ajna":         [4, 11, 17, 24, 43, 47],
    "throat":       [8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62],
    "g":            [1, 2, 7, 10, 13, 15, 25, 46],
    "heart":        [21, 26, 40, 51],
    "spleen":       [18, 28, 32, 44, 48, 50, 57],
    "sacral":       [3, 5, 9, 14, 27, 29, 34, 42, 59],
    "solar_plexus": [6, 22, 30, 36, 37, 49, 55],
    "root":         [19, 38, 39, 41, 52, 53, 54, 58, 60],
}

# Catégorisation des centres pour la logique du Type :
# - Moteurs (4) : Heart, Root, Sacral, Solar Plexus
# - Awareness (3) : Ajna, Splenic, Solar Plexus (le SP est à la fois moteur et awareness)
# - Pressure (2) : Head, Root
# - Manifesting (1) : Throat
CENTRES_MOTEURS: Set[str] = {"heart", "root", "sacral", "solar_plexus"}

# Validation structurelle au chargement
_all_gates: List[int] = []
for _gates in CENTRES.values():
    _all_gates.extend(_gates)

assert len(_all_gates) == 64, "Il doit y avoir exactement 64 gates au total"
assert len(set(_all_gates)) == 64, "Chaque gate ne doit appartenir qu'à un seul centre"
assert set(_all_gates) == set(range(1, 65)), "Toutes les gates de 1 à 64 doivent être présentes"

# Construction d'un mapping inverse : gate -> centre
GATE_TO_CENTRE: Dict[int, str] = {}
for _centre, _gates in CENTRES.items():
    for _gate in _gates:
        GATE_TO_CENTRE[_gate] = _centre


def calculer_centres_definis(canaux_actifs: List[Tuple[int, int]]) -> Set[str]:
    """
    Détermine l'ensemble des centres définis à partir des canaux actifs.

    Un centre est défini dès qu'au moins un canal qui le traverse est
    complet (ses deux gates allumées). Si plusieurs canaux le traversent,
    il reste défini (un seul suffit).
    """
    centres_definis: Set[str] = set()
    for gate_a, gate_b in canaux_actifs:
        centres_definis.add(GATE_TO_CENTRE[gate_a])
        centres_definis.add(GATE_TO_CENTRE[gate_b])
    return centres_definis


def calculer_centres_non_definis(canaux_actifs: List[Tuple[int, int]]) -> Set[str]:
    """
    Retourne les centres qui ne sont PAS définis (complément).
    Utile pour la logique d'autorité et le calcul du type.
    """
    definis = calculer_centres_definis(canaux_actifs)
    return set(CENTRES.keys()) - definis


def centres_moteurs_definis(canaux_actifs: List[Tuple[int, int]]) -> Set[str]:
    """
    Retourne les centres moteurs définis (Heart, Root, Sacral, Solar Plexus).
    Crucial pour déterminer le Type (Manifesteur, Générateur, etc.).
    """
    return calculer_centres_definis(canaux_actifs) & CENTRES_MOTEURS


def throat_connecte_a_moteur(canaux_actifs: List[Tuple[int, int]]) -> bool:
    """
    Détermine si le Throat est connecté à un centre moteur via une chaîne
    de canaux actifs. C'est le critère central pour distinguer un Manifesteur
    (Throat motorisé) d'un Projecteur (Throat défini mais non motorisé) ou
    d'un Générateur (Sacral défini).

    Utilise un parcours de graphe (BFS) : on part du Throat, on explore
    tous les centres atteignables via des canaux actifs, et on regarde si
    un moteur est dans l'ensemble atteignable.
    """
    centres_definis = calculer_centres_definis(canaux_actifs)
    if "throat" not in centres_definis:
        return False

    # Construire le graphe des connexions actives entre centres
    voisins: Dict[str, Set[str]] = {c: set() for c in CENTRES}
    for gate_a, gate_b in canaux_actifs:
        centre_a = GATE_TO_CENTRE[gate_a]
        centre_b = GATE_TO_CENTRE[gate_b]
        voisins[centre_a].add(centre_b)
        voisins[centre_b].add(centre_a)

    # BFS depuis Throat
    visites: Set[str] = set()
    a_visiter: List[str] = ["throat"]
    while a_visiter:
        centre = a_visiter.pop(0)
        if centre in visites:
            continue
        visites.add(centre)
        a_visiter.extend(voisins[centre] - visites)

    return bool(visites & CENTRES_MOTEURS)
