# backend/app/services/human_design/type_hd.py
"""
Détermination du Type Human Design et de sa Stratégie associée.

NOTE : ce fichier s'appelle `type_hd.py` et non `types.py` pour éviter
le conflit avec le module standard Python `types`. Sans ça, l'import
`from typing import ...` provoque une erreur circulaire dans tout le
package.

VALIDATION EMPIRIQUE EFFECTUEE (juin 2026) :
Règles de classification confirmées par multiples sources indépendantes :
- Jovian Archive (référence officielle de Ra Uru Hu)
- Genetic Matrix (geneticmatrix.com/learn-hub)
- Free Human Design Chart (freehumandesignchart.com)
- Eidolon Human Design (medium)
- Just Follow Joy
- Human Design Hub

Aucune divergence détectée entre les sources.

Cas de référence Henry Dupont (charte Jovian Archive officielle) :
- Sacral non défini + Throat connecté à un moteur (Heart, Solar Plexus)
- Type attendu : Manifesteur, Stratégie : Informer
"""
from typing import List, Tuple, Dict
from app.services.human_design.centers import (
    calculer_centres_definis,
    throat_connecte_a_moteur,
)


# Les 5 Types du Human Design avec leurs noms français
TYPES_HD = {
    "MANIFESTEUR": "Manifesteur",
    "GENERATEUR": "Générateur",
    "GENERATEUR_MANIFESTANT": "Générateur Manifestant",
    "PROJECTEUR": "Projecteur",
    "REFLECTEUR": "Réflecteur",
}

# Stratégie associée à chaque Type (convention Jovian Archive)
STRATEGIES: Dict[str, str] = {
    "Manifesteur": "Informer avant d'agir",
    "Générateur": "Répondre à ce qui se présente",
    "Générateur Manifestant": "Répondre puis informer",
    "Projecteur": "Attendre l'invitation",
    "Réflecteur": "Attendre un cycle lunaire (28 jours)",
}

# Signature (état naturel quand on suit sa stratégie) - utile pour la synthèse IA
SIGNATURES: Dict[str, str] = {
    "Manifesteur": "Paix",
    "Générateur": "Satisfaction",
    "Générateur Manifestant": "Satisfaction",
    "Projecteur": "Succès",
    "Réflecteur": "Surprise",
}

# Pas-Soi (état de déconnexion quand on ne suit pas sa stratégie)
NON_SOI: Dict[str, str] = {
    "Manifesteur": "Colère",
    "Générateur": "Frustration",
    "Générateur Manifestant": "Frustration et colère",
    "Projecteur": "Amertume",
    "Réflecteur": "Déception",
}


def determiner_type(canaux_actifs: List[Tuple[int, int]]) -> str:
    """
    Détermine le Type Human Design à partir des canaux actifs.

    Règles de classification :
    1. Réflecteur : 0 centre défini (tous blancs)
    2. Générateur Manifestant : Sacral défini ET Throat connecté à un moteur
    3. Générateur : Sacral défini ET Throat non connecté à un moteur
    4. Manifesteur : Sacral non défini ET Throat connecté à un moteur
       (le moteur connecté est donc Heart, Solar Plexus ou Root)
    5. Projecteur : Sacral non défini ET Throat non connecté à un moteur
    """
    centres_definis = calculer_centres_definis(canaux_actifs)

    # Cas 1 : Réflecteur
    if len(centres_definis) == 0:
        return TYPES_HD["REFLECTEUR"]

    sacral_defini = "sacral" in centres_definis
    throat_motorise = throat_connecte_a_moteur(canaux_actifs)

    # Cas 2 et 3 : Générateurs (Sacral défini)
    if sacral_defini:
        if throat_motorise:
            return TYPES_HD["GENERATEUR_MANIFESTANT"]
        return TYPES_HD["GENERATEUR"]

    # Cas 4 et 5 : Non-Sacral
    if throat_motorise:
        return TYPES_HD["MANIFESTEUR"]
    return TYPES_HD["PROJECTEUR"]


def determiner_strategie(type_hd: str) -> str:
    """Retourne la stratégie associée à un Type."""
    return STRATEGIES.get(type_hd, "")


def determiner_signature(type_hd: str) -> str:
    """Retourne la signature (état naturel) associée à un Type."""
    return SIGNATURES.get(type_hd, "")


def determiner_non_soi(type_hd: str) -> str:
    """Retourne le 'Pas-Soi' (état de déconnexion) associé à un Type."""
    return NON_SOI.get(type_hd, "")
