"""Service de numérologie - calcul chemin de vie, expression, intime."""

from datetime import date

# Table de correspondance lettres → chiffres (méthode pythagoricienne)
LETTRES = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

VOYELLES = set('AEIOUY')
NOMBRES_MAITRES = {11, 22, 33}


def reduire(n: int) -> int:
    """Réduit un entier à 1-9 ou nombre maître (11, 22, 33)."""
    while n > 9 and n not in NOMBRES_MAITRES:
        n = sum(int(d) for d in str(n))
    return n


def _somme_chiffres(n: int) -> int:
    """Somme les chiffres d'un entier (sans réduction maître)."""
    return sum(int(d) for d in str(n))


def calcul_chemin_vie(date_naissance: date) -> int:
    """
    Calcule le chemin de vie.
    Méthode : sommer tous les chiffres de la date (JJMMAAAA) puis réduire.
    Exemple : 12/06/1990 → 1+2+0+6+1+9+9+0 = 28 → 2+8=10 → 1+0=1
    """
    chiffres = f"{date_naissance.day:02d}{date_naissance.month:02d}{date_naissance.year}"
    total = sum(int(c) for c in chiffres)
    return reduire(total)


def calcul_expression(nom: str) -> int:
    """
    Calcule le nombre d'expression (toutes les lettres du nom complet).
    Exemple : 'ALICE' → 1+3+9+3+5 = 21 → 3
    """
    nom_clean = nom.upper().replace(' ', '').replace('-', '')
    total = sum(LETTRES.get(c, 0) for c in nom_clean if c.isalpha())
    return reduire(total)


def calcul_intime(nom: str) -> int:
    """
    Calcule le nombre intime (voyelles uniquement).
    Exemple : 'ALICE' → A(1) + I(9) + E(5) = 15 → 6
    """
    nom_clean = nom.upper().replace(' ', '').replace('-', '')
    total = sum(LETTRES.get(c, 0) for c in nom_clean if c in VOYELLES)
    return reduire(total)


def calculer(prenom: str, nom_famille: str, date_naissance: date) -> dict:
    """Retourne les 3 résultats numérologie pour un profil."""
    nom_complet = f"{prenom} {nom_famille}"
    return {
        "chemin_vie": calcul_chemin_vie(date_naissance),
        "expression": calcul_expression(nom_complet),
        "intime": calcul_intime(nom_complet),
    }
