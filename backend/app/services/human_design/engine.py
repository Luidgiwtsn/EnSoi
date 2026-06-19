# backend/app/services/human_design/engine.py
"""
Orchestrateur du moteur Human Design.

Point d'entrée unique qui assemble les trois modules de calcul :
- ephemerides.py : positions astronomiques (pyswisseph)
- gates.py : conversion degrés → gates I-Ching
- channels.py : détection des canaux actifs

Statut actuel (juin 2026) :
- Calcul des gates : OPERATIONNEL (validé empiriquement, 9/10 points)
- Calcul des canaux : OPERATIONNEL (validé sur cas Henry Dupont, 3/3 canaux)
- Calcul Type / Stratégie / Profil / Autorité : NON IMPLEMENTE (à venir)

Tant que la logique métier complète (centres, type, autorité) n'est pas
écrite, cette fonction retourne `donnees_completes=False` même quand
heure + pays + fuseau sont fournis. Les champs type_hd, strategie, profil
et autorite sont vides en attendant — clairement marqués pour ne pas
induire en erreur le frontend ou l'IA.
"""
from datetime import date, time
from typing import Optional

from app.services.human_design.ephemerides import calculer_double_carte
from app.services.human_design.gates import positions_vers_gates
from app.services.human_design.channels import calculer_canaux_actifs


def calculer(
    date_naissance: date,
    heure_naissance: Optional[time] = None,
    pays_naissance: Optional[str] = None,
    fuseau_horaire_naissance: Optional[str] = None,
) -> dict:
    """
    Calcule les données Human Design à partir de la date/heure/lieu de
    naissance. Compatible avec la signature attendue par routers/profils.py.

    Retourne un dict aux clés :
    - type_hd : str (vide tant que la logique métier n'est pas implémentée)
    - strategie : str (vide pour la même raison)
    - profil : str (vide)
    - autorite : str (vide)
    - donnees_completes : bool (toujours False tant que la logique métier
      n'est pas implémentée, même quand toutes les entrées sont fournies)

    Si l'heure ou le fuseau horaire ne sont pas fournis, on ne peut pas
    calculer la carte astronomique, et donnees_completes reste False.
    """
    # Si on manque d'une donnée critique, on ne tente pas le calcul
    if heure_naissance is None or fuseau_horaire_naissance is None:
        return {
            "type_hd": "",
            "strategie": "",
            "profil": "",
            "autorite": "",
            "donnees_completes": False,
        }

    # Calcul astronomique + traduction en gates et canaux
    # (résultats stockés mais pas encore exploités pour déterminer le type)
    positions = calculer_double_carte(
        date_naissance, heure_naissance, fuseau_horaire_naissance
    )
    gates_conscientes = positions_vers_gates(positions["conscient"])
    gates_inconscientes = positions_vers_gates(positions["inconscient"])
    canaux_actifs = calculer_canaux_actifs(gates_conscientes, gates_inconscientes)

    # TODO : implémenter centers.py + logique Type/Strategie/Profil/Autorite
    # Pour l'instant, on retourne des champs vides avec donnees_completes=False
    # pour que le frontend affiche "Fournissez heure et lieu pour voir votre
    # Human Design" même quand les données sont fournies — tant que la
    # logique métier complète n'est pas livrée.
    return {
        "type_hd": "",
        "strategie": "",
        "profil": "",
        "autorite": "",
        "donnees_completes": False,
        # Données brutes stockées pour la suite (debug et préparation V2)
        "_gates_conscientes": gates_conscientes,
        "_gates_inconscientes": gates_inconscientes,
        "_canaux_actifs": canaux_actifs,
    }
