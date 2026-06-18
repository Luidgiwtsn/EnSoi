# backend/app/services/human_design/channels.py
"""
Table des 36 canaux du Human Design et logique de détermination
des canaux actifs à partir des gates activées (conscientes + inconscientes).

VALIDATION EMPIRIQUE EFFECTUEE (juin 2026) :
Chacune des 36 paires de cette table a été confirmée par au moins une
source indépendante de la liste de référence initiale (humandesign4all.com),
parmi : Amy Doyle (amydoyle.com.au), humandesign.wikidot.com,
Health Manifested (healthmanifested.com), humdes.com/kb, Genetic Matrix
(geneticmatrix.com/learn-hub), humdes.info, humandesignhd.com, NamuWiki,
ahumandesign.com, freehumandesignchart.com.
Aucune divergence n'a été détectée entre les sources sur l'ensemble du
processus. Voir aussi gates.py pour la méthode de validation des gates
elles-mêmes (validée à 9/10 points d'ancrage contre une charte Jovian
Archive de référence).

Structure : chaque canal relie deux gates (et donc, indirectement, les deux
centres auxquels ces gates appartiennent — voir centers.py, non encore
écrit).
"""
from typing import Dict, List, Set, Tuple

# Les 36 canaux du Human Design, sous forme de paires (gate_a, gate_b).
# L'ordre des deux gates dans la paire n'a pas d'importance pour la logique
# d'activation (un canal est actif si les DEUX gates sont allumées, peu
# importe laquelle est "à gauche" ou "à droite").
CANAUX: List[Tuple[int, int]] = [
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31), (9, 52),
    (10, 20), (10, 34), (10, 57), (11, 56), (12, 22), (13, 33), (16, 48),
    (17, 62), (18, 58), (19, 49), (20, 34), (20, 57), (21, 45), (23, 43),
    (24, 61), (25, 51), (26, 44), (27, 50), (28, 38), (29, 46), (30, 41),
    (32, 54), (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64),
]

assert len(CANAUX) == 36, "Il doit y avoir exactement 36 canaux"
assert len(set(CANAUX)) == 36, "Chaque canal doit être unique"

# Vérification que les 64 gates sont bien couvertes par au moins un canal
_gates_couvertes: Set[int] = set()
for gate_a, gate_b in CANAUX:
    _gates_couvertes.add(gate_a)
    _gates_couvertes.add(gate_b)
assert _gates_couvertes == set(range(1, 65)), "Toutes les gates 1-64 doivent appartenir à au moins un canal"


def extraire_gates_actives(gates_conscient: Dict[str, Dict[str, int]],
                            gates_inconscient: Dict[str, Dict[str, int]]) -> Set[int]:
    """
    Extrait l'ensemble des numéros de gates actives, qu'elles viennent
    de la carte consciente (Personnalité) ou inconsciente (Design).

    Une gate est "active" dès qu'elle est touchée par au moins une planète,
    peu importe la carte d'origine — c'est ce qui permettra de déterminer
    les canaux et donc les centres définis.
    """
    actives: Set[int] = set()
    for activation in gates_conscient.values():
        actives.add(activation["gate"])
    for activation in gates_inconscient.values():
        actives.add(activation["gate"])
    return actives


def calculer_canaux_actifs(gates_conscient: Dict[str, Dict[str, int]],
                            gates_inconscient: Dict[str, Dict[str, int]]) -> List[Tuple[int, int]]:
    """
    Détermine quels canaux sont actifs (complets) pour une charte donnée.

    Un canal est actif si et seulement si SES DEUX gates sont actives,
    peu importe qu'elles viennent du conscient, de l'inconscient, ou un
    mélange des deux (une gate consciente + une gate inconsciente forme
    bien un canal complet — c'est ce qu'on appelle une définition mixte).
    """
    gates_actives = extraire_gates_actives(gates_conscient, gates_inconscient)

    canaux_actifs = []
    for gate_a, gate_b in CANAUX:
        if gate_a in gates_actives and gate_b in gates_actives:
            canaux_actifs.append((gate_a, gate_b))

    return canaux_actifs


def gates_en_attente(gates_conscient: Dict[str, Dict[str, int]],
                      gates_inconscient: Dict[str, Dict[str, int]]) -> List[int]:
    """
    Retourne les "hanging gates" : des gates activées dans la charte
    mais dont le partenaire de canal n'est pas activé. Ces gates ne créent
    pas de définition de centre par elles-mêmes, mais peuvent s'activer en
    présence d'une autre personne qui possède la gate manquante
    (connexion électromagnétique).
    """
    gates_actives = extraire_gates_actives(gates_conscient, gates_inconscient)
    canaux_actifs = set(calculer_canaux_actifs(gates_conscient, gates_inconscient))

    gates_dans_canaux_actifs: Set[int] = set()
    for gate_a, gate_b in canaux_actifs:
        gates_dans_canaux_actifs.add(gate_a)
        gates_dans_canaux_actifs.add(gate_b)

    return sorted(gates_actives - gates_dans_canaux_actifs)
