# backend/app/services/human_design/engine.py
"""
Orchestrateur du moteur Human Design.

Point d'entrée unique qui assemble tous les modules de calcul :
- ephemerides.py : positions astronomiques (pyswisseph)
- gates.py : conversion degrés -> gates I-Ching
- channels.py : détection des canaux actifs
- centers.py : centres définis à partir des canaux
- type_hd.py : détermination du Type et de sa Stratégie
- authority.py : détermination de l'Autorité Intérieure
- profile_hd.py : calcul du Profil (lignes Soleil conscient/inconscient)

Statut : OPÉRATIONNEL (juin 2026).

Validation empirique sur le cas de référence Henry Dupont (1er janvier
2026, 12:00 UTC, Londres) - 4/4 indicateurs conformes à la charte
officielle Jovian Archive :
- Type : Manifesteur
- Stratégie : Informer
- Autorité : Plexus solaire (Émotionnelle)
- Profil : 2/4 (Ermite / Opportuniste)

Si l'heure ou le fuseau horaire ne sont pas fournis, le calcul
astronomique est impossible et la fonction retourne donnees_completes=False
avec des champs vides. Sinon, donnees_completes=True et les 4 indicateurs
sont remplis.
"""
from datetime import date, time
from typing import Optional

from app.services.human_design.ephemerides import calculer_double_carte
from app.services.human_design.gates import positions_vers_gates
from app.services.human_design.channels import calculer_canaux_actifs
from app.services.human_design.centers import calculer_centres_definis
from app.services.human_design.type_hd import (
    determiner_type,
    determiner_strategie,
)
from app.services.human_design.authority import determiner_autorite
from app.services.human_design.profile_hd import determiner_profil


def calculer(
    date_naissance: date,
    heure_naissance: Optional[time] = None,
    pays_naissance: Optional[str] = None,
    fuseau_horaire_naissance: Optional[str] = None,
) -> dict:
    """
    Calcule les données Human Design complètes à partir des données de
    naissance. Compatible avec la signature attendue par routers/profils.py.

    Retourne un dict aux clés :
    - type_hd : str (les 5 types possibles, vide si données manquantes)
    - strategie : str (la stratégie associée au type)
    - profil : str (notation "X/Y" + nom, ex "2/4 - Ermite / Opportuniste")
    - autorite : str (une des 7 autorités possibles)
    - donnees_completes : bool (True seulement si heure + fuseau fournis)

    Données brutes additionnelles (préfixées _) conservées pour debug
    et préparation des fonctionnalités V2 (centres, gates détaillées) :
    - _gates_conscientes, _gates_inconscientes : dict {planete: {gate, line}}
    - _canaux_actifs : liste de tuples (gate_a, gate_b)
    - _centres_definis : set des centres définis
    """
    # Si on manque d'une donnée critique, on ne peut pas calculer la
    # carte astronomique. On retourne un résultat partiel explicite.
    if heure_naissance is None or fuseau_horaire_naissance is None:
        return {
            "type_hd": "",
            "strategie": "",
            "profil": "",
            "autorite": "",
            "donnees_completes": False,
        }

    # 1. Calcul astronomique (pyswisseph, mode Moshier)
    positions = calculer_double_carte(
        date_naissance, heure_naissance, fuseau_horaire_naissance
    )

    # 2. Traduction degrés -> gates/lignes
    gates_conscientes = positions_vers_gates(positions["conscient"])
    gates_inconscientes = positions_vers_gates(positions["inconscient"])

    # 3. Détection des canaux actifs (les deux gates allumées)
    canaux_actifs = calculer_canaux_actifs(gates_conscientes, gates_inconscientes)

    # 4. Détermination des centres définis (au moins un canal les traverse)
    centres_definis = calculer_centres_definis(canaux_actifs)

    # 5. Détermination du Type et de sa Stratégie
    type_hd = determiner_type(canaux_actifs)
    strategie = determiner_strategie(type_hd)

    # 6. Détermination de l'Autorité (hiérarchie stricte des centres)
    autorite = determiner_autorite(canaux_actifs)

    # 7. Calcul du Profil (lignes Soleil conscient + inconscient)
    profil_data = determiner_profil(
        gates_conscientes["soleil"]["line"],
        gates_inconscientes["soleil"]["line"],
    )
    profil_str = f"{profil_data['notation']} - {profil_data['nom']}"

    return {
        "type_hd": type_hd,
        "strategie": strategie,
        "profil": profil_str,
        "autorite": autorite,
        "donnees_completes": True,
        # Données brutes pour debug et V2
        "_gates_conscientes": gates_conscientes,
        "_gates_inconscientes": gates_inconscientes,
        "_canaux_actifs": canaux_actifs,
        "_centres_definis": list(centres_definis),
    }
