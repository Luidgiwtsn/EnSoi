"""Tests unitaires — service Profil Cognitif."""

import pytest
from collections import Counter
from app.services.profil_cognitif import (
    calculer,
    get_questions,
    TYPES_COGNITIFS,
    QUESTIONS,
)


# --- get_questions() ---

def test_get_questions_retourne_12_questions():
    assert len(get_questions()) == 12

def test_questions_ont_les_bons_champs():
    for q in get_questions():
        assert 'id' in q
        assert 'axe' in q
        assert 'texte' in q
        assert 'pole_a' in q
        assert 'pole_b' in q

def test_questions_3_par_axe():
    axes = Counter(q['axe'] for q in QUESTIONS)
    assert axes['energie'] == 3
    assert axes['perception'] == 3
    assert axes['decision'] == 3
    assert axes['organisation'] == 3


# --- calculer() ---

def test_calculer_tout_pole_a():
    """Toutes réponses à 1 → INFJ."""
    result = calculer([1] * 12)
    assert result['type_cognitif'] == 'INFJ'

def test_calculer_tout_pole_b():
    """Toutes réponses à 5 → ESTP."""
    result = calculer([5] * 12)
    assert result['type_cognitif'] == 'ESTP'

def test_calculer_neutre_donne_pole_a():
    """Position 3 (neutre) → pôle A par défaut → INFJ."""
    result = calculer([3] * 12)
    assert result['type_cognitif'] == 'INFJ'

def test_calculer_neutre_score_51():
    """Position 3 (neutre) → score 51% pour cohérence visuelle."""
    result = calculer([3] * 12)
    for axe in result['dimensions'].values():
        assert axe['score_pourcentage'] == 51

def test_calculer_retourne_nom_profil():
    result = calculer([1] * 12)
    assert result['nom_profil'] == 'Le Protecteur'

def test_calculer_type_valide():
    result = calculer([1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2])
    assert result['type_cognitif'] in TYPES_COGNITIFS

def test_calculer_dimensions_contiennent_bons_champs():
    result = calculer([1] * 12)
    for axe in ['energie', 'perception', 'decision', 'organisation']:
        assert axe in result['dimensions']
        assert 'dominant' in result['dimensions'][axe]
        assert 'lettre' in result['dimensions'][axe]
        assert 'score_pourcentage' in result['dimensions'][axe]

def test_calculer_score_pourcentage_valide():
    result = calculer([1] * 12)
    for axe in result['dimensions'].values():
        assert 0 <= axe['score_pourcentage'] <= 100

def test_calculer_erreur_mauvais_nombre_reponses():
    with pytest.raises(ValueError):
        calculer([1, 2, 3])

def test_calculer_erreur_valeur_hors_range():
    with pytest.raises(ValueError):
        calculer([6] * 12)
