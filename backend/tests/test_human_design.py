"""Tests unitaires - service Human Design (moteur complet).

Ces tests valident chaque brique du moteur Human Design indépendamment
des autres (tests unitaires) puis l'orchestrateur final (tests
d'intégration), en se basant sur le cas de référence Henry Dupont
(charte officielle Jovian Archive) et sur des scénarios théoriques
pour couvrir les 5 types et 7 autorités.

Cas de référence Henry Dupont (01/01/2026 12:00 UTC à Londres) :
- Type:      Manifesteur
- Stratégie: Informer
- Autorité:  Émotionnelle (Plexus solaire)
- Profil:    2/4 (Ermite / Opportuniste)
- Canaux:    [(10, 20), (35, 36), (37, 40)]
- Centres:   g, heart, solar_plexus, throat
"""
from datetime import date, time

from app.services.human_design import calculer
from app.services.human_design.centers import (
    CENTRES,
    CENTRES_MOTEURS,
    GATE_TO_CENTRE,
    calculer_centres_definis,
    calculer_centres_non_definis,
    centres_moteurs_definis,
    throat_connecte_a_moteur,
)
from app.services.human_design.channels import CANAUX
from app.services.human_design.type_hd import (
    TYPES_HD,
    STRATEGIES,
    SIGNATURES,
    NON_SOI,
    determiner_type,
    determiner_strategie,
    determiner_signature,
    determiner_non_soi,
)
from app.services.human_design.authority import (
    AUTORITES,
    determiner_autorite,
)
from app.services.human_design.profile_hd import (
    LIGNES,
    PROFILS_VALIDES,
    determiner_profil,
)


# Canaux activés sur la charte Henry Dupont (référence Jovian Archive)
CANAUX_HENRY = [(10, 20), (35, 36), (37, 40)]


# --- centers.py : structure de la table ---

def test_centres_total_64_gates():
    """La somme des gates des 9 centres doit couvrir les 64 gates."""
    total = sum(len(v) for v in CENTRES.values())
    assert total == 64


def test_centres_pas_de_doublons():
    """Chaque gate doit appartenir à un seul centre."""
    all_gates = []
    for v in CENTRES.values():
        all_gates.extend(v)
    assert len(all_gates) == len(set(all_gates))


def test_centres_toutes_gates_couvertes():
    """Les 64 gates (1 à 64) doivent toutes être présentes."""
    all_gates = set()
    for v in CENTRES.values():
        all_gates.update(v)
    assert all_gates == set(range(1, 65))


def test_centres_9_au_total():
    """Il doit y avoir exactement 9 centres."""
    assert len(CENTRES) == 9


def test_moteurs_au_nombre_de_4():
    """Les centres moteurs doivent être 4 (Heart, Root, Sacral, Solar Plexus)."""
    assert CENTRES_MOTEURS == {"heart", "root", "sacral", "solar_plexus"}


def test_gate_to_centre_coherent_avec_centres():
    """Le mapping inverse doit être cohérent avec la table directe."""
    for gate in range(1, 65):
        centre = GATE_TO_CENTRE[gate]
        assert gate in CENTRES[centre]


# --- centers.py : compatibilité avec les canaux ---

def test_chaque_canal_relie_deux_centres_differents():
    """Un canal doit toujours relier 2 gates de centres différents."""
    for gate_a, gate_b in CANAUX:
        assert GATE_TO_CENTRE[gate_a] != GATE_TO_CENTRE[gate_b]


# --- centers.py : Henry Dupont ---

def test_henry_centres_definis():
    """Henry Dupont a 4 centres définis : g, heart, solar_plexus, throat."""
    definis = calculer_centres_definis(CANAUX_HENRY)
    assert definis == {"g", "heart", "solar_plexus", "throat"}


def test_henry_centres_non_definis():
    """Henry Dupont a 5 centres non définis : ajna, head, root, sacral, spleen."""
    non_definis = calculer_centres_non_definis(CANAUX_HENRY)
    assert non_definis == {"ajna", "head", "root", "sacral", "spleen"}


def test_henry_moteurs_definis():
    """Henry Dupont a 2 moteurs définis : heart et solar_plexus."""
    moteurs = centres_moteurs_definis(CANAUX_HENRY)
    assert moteurs == {"heart", "solar_plexus"}


def test_henry_throat_connecte_a_moteur():
    """Henry Dupont est Manifesteur : Throat connecté à un moteur."""
    assert throat_connecte_a_moteur(CANAUX_HENRY) is True


# --- centers.py : cas limites ---

def test_reflecteur_aucun_centre_defini():
    """Sans aucun canal actif, aucun centre n'est défini (Réflecteur)."""
    assert calculer_centres_definis([]) == set()


def test_throat_non_connecte_sans_throat():
    """Si Throat n'est pas défini, throat_connecte_a_moteur retourne False."""
    canaux_sans_throat = [(34, 57)]  # Sacral + Spleen, pas de Throat
    assert throat_connecte_a_moteur(canaux_sans_throat) is False


# --- type_hd.py : structure ---

def test_5_types_hd():
    """Il doit y avoir exactement 5 types Human Design."""
    assert len(TYPES_HD) == 5


def test_strategies_pour_chaque_type():
    """Chaque type doit avoir une stratégie associée."""
    for type_nom in TYPES_HD.values():
        assert type_nom in STRATEGIES
        assert STRATEGIES[type_nom] != ""


def test_signatures_pour_chaque_type():
    """Chaque type doit avoir une signature associée."""
    for type_nom in TYPES_HD.values():
        assert type_nom in SIGNATURES


def test_non_soi_pour_chaque_type():
    """Chaque type doit avoir un Pas-Soi associé."""
    for type_nom in TYPES_HD.values():
        assert type_nom in NON_SOI


# --- type_hd.py : les 5 scénarios de classification ---

def test_type_henry_dupont_manifesteur():
    """Cas de référence : Henry Dupont est Manifesteur."""
    assert determiner_type(CANAUX_HENRY) == "Manifesteur"


def test_type_reflecteur_sans_centre_defini():
    """Aucun canal actif → Réflecteur."""
    assert determiner_type([]) == "Réflecteur"


def test_type_generateur_sacral_seul():
    """Sacral défini, Throat non motorisé → Générateur."""
    # Canal 34-57 : Sacral + Spleen, sans Throat
    assert determiner_type([(34, 57)]) == "Générateur"


def test_type_generateur_manifestant_sacral_et_throat():
    """Sacral défini + Throat connecté → Générateur Manifestant."""
    # Canal 34-20 : Sacral + Throat (motorisé via Sacral lui-même)
    assert determiner_type([(34, 20)]) == "Générateur Manifestant"


def test_type_manifesteur_sans_sacral_throat_motorise():
    """Sacral non défini + Throat connecté à un moteur → Manifesteur."""
    # Canal 21-45 : Heart + Throat (motorisé via Heart)
    assert determiner_type([(21, 45)]) == "Manifesteur"


def test_type_projecteur_sans_sacral_sans_throat_motorise():
    """Sacral non défini + Throat non motorisé → Projecteur."""
    # Canal 10-57 : G + Spleen, ni Sacral ni Throat
    assert determiner_type([(10, 57)]) == "Projecteur"


# --- type_hd.py : stratégies, signatures, Pas-Soi ---

def test_strategie_manifesteur():
    assert "Informer" in determiner_strategie("Manifesteur")


def test_strategie_generateur():
    assert "Répondre" in determiner_strategie("Générateur")


def test_signature_manifesteur_paix():
    assert determiner_signature("Manifesteur") == "Paix"


def test_non_soi_manifesteur_colere():
    assert determiner_non_soi("Manifesteur") == "Colère"


# --- authority.py : structure et les 7 autorités ---

def test_7_autorites():
    """Il doit y avoir exactement 7 autorités."""
    assert len(AUTORITES) == 7


def test_henry_dupont_autorite_emotionnelle():
    """Henry Dupont a Solar Plexus défini → Émotionnelle."""
    autorite = determiner_autorite(CANAUX_HENRY)
    assert "Émotionnelle" in autorite
    assert "Plexus solaire" in autorite


def test_autorite_lunaire_pour_reflecteur():
    """Aucun centre défini → Lunaire."""
    assert "Lunaire" in determiner_autorite([])


def test_autorite_sacrale_si_sacral_sans_solar_plexus():
    """Sacral défini sans SP → Sacrale."""
    # Canal 34-57 : Sacral + Spleen, pas de Solar Plexus
    assert "Sacrale" == determiner_autorite([(34, 57)])


def test_autorite_splenique_si_spleen_seul():
    """Spleen défini sans SP ni Sacral → Splénique."""
    # Canal 10-57 : G + Spleen
    assert "Splénique" == determiner_autorite([(10, 57)])


def test_autorite_ego_si_heart_seul():
    """Heart défini sans SP/Sacral/Spleen → Ego."""
    # Canal 21-45 : Heart + Throat
    assert "Ego" in determiner_autorite([(21, 45)])


def test_autorite_auto_projetee_si_g_seul():
    """G défini sans SP/Sacral/Spleen/Heart → Auto-projetée."""
    # Canal 1-8 : G + Throat
    assert "Auto-projetée" in determiner_autorite([(1, 8)])


def test_autorite_mentale_si_que_centres_secondaires():
    """Aucun des centres d'autorité + autres centres définis → Mentale."""
    # Canal 4-63 : Ajna + Head, aucun des centres d'autorité
    assert "Mentale" in determiner_autorite([(4, 63)])


def test_autorite_emotionnelle_prioritaire_sur_sacrale():
    """Si SP ET Sacral définis, l'autorité est Émotionnelle (priorité hiérarchique)."""
    # 35-36 active SP, 34-57 active Sacral
    canaux = [(35, 36), (34, 57)]
    assert "Émotionnelle" in determiner_autorite(canaux)


# --- profile_hd.py : structure ---

def test_12_profils_valides():
    """Il doit y avoir exactement 12 profils valides."""
    assert len(PROFILS_VALIDES) == 12


def test_6_lignes_archetypes():
    """Il doit y avoir 6 archétypes de ligne."""
    assert len(LIGNES) == 6
    assert set(LIGNES.keys()) == {1, 2, 3, 4, 5, 6}


def test_profil_henry_dupont_2_sur_4():
    """Henry Dupont : Soleil conscient ligne 2 + Soleil inconscient ligne 4 = 2/4."""
    result = determiner_profil(2, 4)
    assert result["notation"] == "2/4"
    assert result["valide"] is True
    assert "Ermite" in result["nom"]
    assert "Opportuniste" in result["nom"]


def test_profil_invalide_marque_comme_tel():
    """Une combinaison hors des 12 standards doit être marquée valide=False."""
    result = determiner_profil(1, 1)
    assert result["valide"] is False
    assert result["notation"] == "1/1"


def test_tous_profils_valides_marques_True():
    """Les 12 profils standards doivent tous être marqués valide=True."""
    for (l1, l2) in PROFILS_VALIDES:
        result = determiner_profil(l1, l2)
        assert result["valide"] is True


# --- engine.py : orchestrateur, test d'intégration bout-en-bout ---

def test_engine_donnees_incompletes_si_heure_absente():
    """Sans heure, donnees_completes doit être False."""
    result = calculer(date_naissance=date(1990, 6, 12))
    assert result["donnees_completes"] is False
    assert result["type_hd"] == ""
    assert result["strategie"] == ""
    assert result["autorite"] == ""


def test_engine_donnees_incompletes_si_fuseau_absent():
    """Sans fuseau horaire, donnees_completes doit être False."""
    result = calculer(
        date_naissance=date(1990, 6, 12),
        heure_naissance=time(14, 30),
    )
    assert result["donnees_completes"] is False


def test_engine_henry_dupont_complet():
    """Test d'intégration bout-en-bout : Henry Dupont (cas de référence)."""
    result = calculer(
        date_naissance=date(2026, 1, 1),
        heure_naissance=time(12, 0),
        pays_naissance="United Kingdom",
        fuseau_horaire_naissance="Europe/London",
    )

    assert result["donnees_completes"] is True
    assert result["type_hd"] == "Manifesteur"
    assert "Informer" in result["strategie"]
    assert "Plexus solaire" in result["autorite"]
    assert "2/4" in result["profil"]
    assert "Ermite" in result["profil"]


def test_engine_henry_dupont_canaux_attendus():
    """Henry Dupont : 3 canaux attendus exactement (10-20, 35-36, 37-40)."""
    result = calculer(
        date_naissance=date(2026, 1, 1),
        heure_naissance=time(12, 0),
        pays_naissance="United Kingdom",
        fuseau_horaire_naissance="Europe/London",
    )

    canaux = result["_canaux_actifs"]
    assert len(canaux) == 3
    assert (10, 20) in canaux
    assert (35, 36) in canaux
    assert (37, 40) in canaux


def test_engine_henry_dupont_centres_attendus():
    """Henry Dupont : 4 centres définis exactement (g, heart, solar_plexus, throat)."""
    result = calculer(
        date_naissance=date(2026, 1, 1),
        heure_naissance=time(12, 0),
        pays_naissance="United Kingdom",
        fuseau_horaire_naissance="Europe/London",
    )

    centres = set(result["_centres_definis"])
    assert centres == {"g", "heart", "solar_plexus", "throat"}
