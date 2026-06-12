from datetime import date
from typing import Dict, List, Set
import unicodedata

# Table de correspondance lettres → chiffres
LETTRES: Dict[str, int] = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

VOYELLES: Set[str] = set('AEIOUY')
NOMBRES_MAITRES: Set[int] = {11, 22, 33}


def _nettoyer_texte(texte: str) -> str:
    """Met en majuscules, retire les espaces, tirets et SURTOUT les accents."""
    # Supprime les accents (ex: É -> E, Ç -> C)
    texte_sans_accent = ''.join(
        c for c in unicodedata.normalize('NFD', texte)
        if unicodedata.category(c) != 'Mn'
    )
    return texte_sans_accent.upper().replace(' ', '').replace('-', '')


def reduire(n: int) -> int:
    """Réduit un entier à 1-9 ou nombre maître (11, 22, 33)."""
    while n > 9 and n not in NOMBRES_MAITRES:
        n = sum(int(d) for d in str(n))
    return n


def calcul_chemin_vie(date_naissance: date) -> int:
    chiffres = f"{date_naissance.day:02d}{date_naissance.month:02d}{date_naissance.year}"
    total = sum(int(c) for c in chiffres)
    return reduire(total)


def calcul_expression(nom: str) -> int:
    nom_clean = _nettoyer_texte(nom)
    total = sum(LETTRES.get(c, 0) for c in nom_clean if c.isalpha())
    return reduire(total)


def calcul_intime(nom: str) -> int:
    nom_clean = _nettoyer_texte(nom)
    total = sum(LETTRES.get(c, 0) for c in nom_clean if c in VOYELLES)
    return reduire(total)


def calcul_realisation(nom: str) -> int:
    """
    NOUVEAU : Calcule le nombre de réalisation (consonnes uniquement).
    """
    nom_clean = _nettoyer_texte(nom)
    total = sum(LETTRES.get(c, 0) for c in nom_clean if c.isalpha() and c not in VOYELLES)
    return reduire(total)


def calculer(prenom: str, nom_famille: str, date_naissance: date) -> dict:
    nom_complet = f"{prenom} {nom_famille}"
    return {
        "chemin_vie": calcul_chemin_vie(date_naissance),
        "expression": calcul_expression(nom_complet),
        "intime": calcul_intime(nom_complet),
        "realisation": calcul_realisation(nom_complet),  # Ajouté au dictionnaire final
    }
