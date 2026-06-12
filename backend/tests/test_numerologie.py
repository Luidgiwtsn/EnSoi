"""Tests unitaires — service numérologie."""

from datetime import date
from app.services.numerologie import (
    reduire,
    calcul_chemin_vie,
    calcul_expression,
    calcul_intime,
    calcul_realisation,
    calculer,
)


# --- reduire() ---

def test_reduire_chiffre_simple():
    assert reduire(5) == 5

def test_reduire_nombre_standard():
    # 2+9=11 → nombre maître → on s'arrête
    assert reduire(29) == 11

def test_reduire_nombre_maitre_11():
    assert reduire(11) == 11  # ne se réduit pas

def test_reduire_nombre_maitre_22():
    assert reduire(22) == 22

def test_reduire_nombre_maitre_33():
    assert reduire(33) == 33

def test_reduire_normal():
    # 3+8=11 → nombre maître → on s'arrête  
    assert reduire(38) == 11

def test_reduire_35():
    assert reduire(35) == 8   # 3+5=8


# --- calcul_chemin_vie() ---

def test_chemin_vie_1990_06_12():
    """12/06/1990 → 1+2+0+6+1+9+9+0 = 28 → 2+8=10 → 1+0=1"""
    assert calcul_chemin_vie(date(1990, 6, 12)) == 1

def test_chemin_vie_2000_01_01():
    assert calcul_chemin_vie(date(2000, 1, 1)) == 4


# --- calcul_expression() ---

def test_expression_lettres_simples():
    # 'ALICE' : A=1, L=3, I=9, C=3, E=5 → 21 → 3
    assert calcul_expression('Alice') == 3

def test_expression_avec_espace():
    # Le nom complet avec espace doit fonctionner
    result = calcul_expression('Alice Martin')
    assert isinstance(result, int)
    assert 1 <= result <= 33


# --- calcul_intime() ---

def test_intime_alice():
    # 'ALICE' voyelles : A=1, I=9, E=5 → 15 → 6
    assert calcul_intime('Alice') == 6

def test_intime_resultat_valide():
    result = calcul_intime('Jean')
    assert isinstance(result, int)
    assert 1 <= result <= 33

def test_calculer_retourne_quatre_valeurs():
    """calculer() retourne chemin_vie, expression, intime et realisation."""
    result = calculer('Alice', 'Martin', date(1990, 6, 12))
    assert 'chemin_vie' in result
    assert 'expression' in result
    assert 'intime' in result
    assert 'realisation' in result
    assert all(isinstance(v, int) for v in result.values())
    
def test_realisation_alice_martin():
    """Consonnes uniquement, accents gérés."""
    result = calcul_realisation('Alice Martin')
    assert isinstance(result, int)
    assert 1 <= result <= 33

def test_expression_avec_accent():
    """Les accents doivent être normalisés — Chloé = Chloe."""
    assert calcul_expression('Chloé Dupont') == calcul_expression('Chloe Dupont')
