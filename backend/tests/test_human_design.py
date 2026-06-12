"""Tests unitaires — service Human Design."""

from datetime import date, time
from app.services.human_design import (
    determiner_type,
    determiner_profil,
    calculer,
    TYPES,
    STRATEGIES,
    PROFILS,
    AUTORITES_PAR_TYPE,
)

TYPES_VALIDES = set(TYPES)
PROFILS_VALIDES = set(PROFILS)


# --- determiner_type() ---

def test_type_retourne_valeur_valide():
    result = determiner_type(date(1990, 6, 12))
    assert result in TYPES_VALIDES

def test_type_deterministe():
    """Même date → même type."""
    d = date(1990, 6, 12)
    assert determiner_type(d) == determiner_type(d)

def test_type_different_selon_date():
    """Plusieurs dates donnent des types différents."""
    types = {determiner_type(date(1990 + i, (i % 12) + 1, (i % 28) + 1)) for i in range(20)}
    assert len(types) > 1


# --- determiner_profil() ---

def test_profil_retourne_valeur_valide():
    result = determiner_profil(date(1990, 6, 12))
    assert result in PROFILS_VALIDES

def test_profil_deterministe():
    d = date(1990, 6, 12)
    assert determiner_profil(d) == determiner_profil(d)

def test_profil_format_correct():
    """Le profil est au format X/Y."""
    result = determiner_profil(date(1990, 6, 12))
    assert '/' in result
    parties = result.split('/')
    assert len(parties) == 2
    assert all(p.isdigit() for p in parties)


# --- calculer() ---

def test_calculer_retourne_quatre_cles():
    result = calculer(date(1990, 6, 12))
    assert 'type_hd' in result
    assert 'strategie' in result
    assert 'profil' in result
    assert 'autorite' in result

def test_calculer_autorite_coherente_avec_type():
    """L'autorité retournée est compatible avec le type."""
    result = calculer(date(1990, 6, 12))
    autorites_valides = AUTORITES_PAR_TYPE[result['type_hd']]
    assert result['autorite'] in autorites_valides

def test_calculer_sans_heure_donnees_incompletes():
    """Sans heure ni lieu, donnees_completes doit être False."""
    result = calculer(date(1990, 6, 12))
    assert result['donnees_completes'] is False

def test_calculer_avec_heure_et_lieu_donnees_completes():
    """Avec heure et lieu, donnees_completes doit être True."""
    result = calculer(
        date(1990, 6, 12),
        heure_naissance=time(14, 30),
        lieu_naissance="Paris, France",
    )
    assert result['donnees_completes'] is True

def test_calculer_coherence_type_strategie():
    """La stratégie retournée correspond bien au type retourné."""
    result = calculer(date(1990, 6, 12))
    assert result['strategie'] == STRATEGIES[result['type_hd']]
