from datetime import date, time
from typing import Dict, List, Optional

# Constantes de configuration
TYPES: List[str] = ["Générateur", "Générateur Manifestant", "Projecteur", "Manifesteur", "Réflecteur"]

STRATEGIES: Dict[str, str] = {
    "Générateur": "Attendre de répondre",
    "Générateur Manifestant": "Attendre de répondre puis informer",
    "Projecteur": "Attendre l'invitation",
    "Manifesteur": "Informer avant d'agir",
    "Réflecteur": "Attendre un cycle lunaire (29 jours)",
}

# Autorités valides par Type pour éviter les profils impossibles
AUTORITES_PAR_TYPE: Dict[str, List[str]] = {
    "Générateur": ["Emotionnelle", "Sacrale"],
    "Générateur Manifestant": ["Emotionnelle", "Sacrale"],
    "Projecteur": ["Emotionnelle", "Splénique", "Ego projeté", "Soi projeté"],
    "Manifesteur": ["Emotionnelle", "Splénique", "Ego manifesté"],
    "Réflecteur": ["Lunaire"],
}

PROFILS: List[str] = [
    "1/3", "1/4", "2/4", "2/5", "3/5", "3/6",
    "4/6", "4/1", "5/1", "5/2", "6/2", "6/3"
]


def determiner_type(date_naissance: date) -> str:
    """
    Détermine le type Human Design par approximation déterministe.
    Distribution corrigée sur base 100 : G=37%, MG=33%, P=21%, M=8%, R=1%
    """
    seed = (date_naissance.year * 13 + date_naissance.month * 7 + date_naissance.day * 3) % 100

    if seed < 37:        # 0 à 36 (37%)
        return "Générateur"
    elif seed < 70:      # 37 à 69 (33%)
        return "Générateur Manifestant"
    elif seed < 91:      # 70 à 90 (21%)
        return "Projecteur"
    elif seed < 99:      # 91 à 98 (8%)
        return "Manifesteur"
    else:                # 99 (1%)
        return "Réflecteur"


def _determiner_autorite_coherente(type_hd: str, date_naissance: date) -> str:
    """Retourne une autorité compatible avec le type calculé."""
    autorites_possibles = AUTORITES_PAR_TYPE[type_hd]
    
    # Si une seule option possible (ex: Réflecteur -> Lunaire)
    if len(autorites_possibles) == 1:
        return autorites_possibles[0]
        
    seed = (date_naissance.year + date_naissance.month * 3 + date_naissance.day * 7) % len(autorites_possibles)
    return autorites_possibles[seed]


def determiner_profil(date_naissance: date) -> str:
    """Détermine le profil parmi les 12 possibles."""
    seed = (date_naissance.day * 5 + date_naissance.month * 11 + date_naissance.year * 2) % 12
    return PROFILS[seed]


def calculer(
    date_naissance: date,
    heure_naissance: Optional[time] = None,
    lieu_naissance: Optional[str] = None,
) -> dict:
    """
    Retourne les 4 résultats Human Design.
    Si heure et lieu fournis : marqué donnees_completes=True.
    Sinon : approximation déterministe + donnees_completes=False.
    """
    type_hd = determiner_type(date_naissance)
    donnees_completes = heure_naissance is not None and lieu_naissance is not None

    return {
        "type_hd": type_hd,
        "strategie": STRATEGIES.get(type_hd, "Inconnue"),
        "profil": determiner_profil(date_naissance),
        "autorite": _determiner_autorite_coherente(type_hd, date_naissance),
        "donnees_completes": donnees_completes,
    }
