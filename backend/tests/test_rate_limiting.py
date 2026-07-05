"""Tests d'intégration pour le rate limiting (slowapi)."""
from unittest.mock import patch

import pytest

from app.rate_limiter import limiter


@pytest.fixture
def limiter_actif():
    """
    Active le rate limiting pour le test et réinitialise les compteurs.
    Par défaut le limiter est désactivé dans conftest.py pour ne pas
    perturber les autres tests d'intégration.
    """
    limiter.enabled = True
    try:
        limiter.reset()
    except (AttributeError, NotImplementedError):
        # Certains backends de storage ne supportent pas reset()
        # — pour MemoryStorage (par défaut), reset() existe.
        pass
    yield
    limiter.enabled = False
    try:
        limiter.reset()
    except (AttributeError, NotImplementedError):
        pass
    

@pytest.fixture
def mock_groq():
    """
    Mock GroqService.generer_synthese pour eviter les vrais appels a
    l'API Groq externe pendant les tests de rate limiting.

    Sans ce mock, chaque requete POST /api/generate declenche un vrai
    appel a Groq (~1.4s en normal, jusqu'a 40s si rate limit externe
    provoque des retries SDK). La fenetre d'une minute du rate limiter
    interne (slowapi) explose alors, et le test echoue a cause d'une
    dependance externe et non d'un bug de slowapi.

    Le mock retourne instantanement une synthese fictive : le test se
    concentre sur ce qu'il doit tester (slowapi), isole de Groq.
    """
    with patch(
        "app.services.groq_service.GroqService.generer_synthese",
        return_value="Synthese mockee pour test rate limiting.",
    ) as mock:
        yield mock

PAYLOAD_LOGIN = {
    "email": "rate-limit-test@example.com",
    "password": "FakePassword1",
}

PAYLOAD_GENERATE = {
    "prenom": "Test",
    "nom_famille": "RateLimit",
    "date_naissance": "1990-01-01",
    "reponses_cognitif": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
}


class TestRateLimitLogin:
    """5 requêtes/minute sur /auth/login (protection contre bruteforce)."""

    def test_5_premieres_requetes_ne_sont_pas_bloquees(self, client, limiter_actif):
        """Les 5 premières passent (peu importe leur code de retour applicatif)."""
        for i in range(5):
            response = client.post("/auth/login", json=PAYLOAD_LOGIN)
            assert response.status_code != 429, (
                f"Requête {i + 1} bloquée trop tôt : {response.status_code}"
            )

    def test_6e_requete_retourne_429(self, client, limiter_actif):
        """La 6ème requête en moins d'une minute doit retourner 429."""
        for _ in range(5):
            client.post("/auth/login", json=PAYLOAD_LOGIN)
        response = client.post("/auth/login", json=PAYLOAD_LOGIN)
        assert response.status_code == 429


class TestRateLimitGenerate:
    """3 requêtes/minute sur /api/generate (protection contre abus IA)."""

    def test_3_premieres_requetes_ne_sont_pas_bloquees(
        self, client, limiter_actif, mock_groq
    ):
        for i in range(3):
            response = client.post("/api/generate", json=PAYLOAD_GENERATE)
            assert response.status_code != 429, (
                f"Requête {i + 1} bloquée trop tôt : {response.status_code}"
            )

    def test_4e_requete_retourne_429(self, client, limiter_actif, mock_groq):
        for _ in range(3):
            client.post("/api/generate", json=PAYLOAD_GENERATE)
        response = client.post("/api/generate", json=PAYLOAD_GENERATE)
        assert response.status_code == 429


class TestLimiterDesactiveParDefaut:
    """Garantit que les autres tests ne sont pas affectés par le rate limiting."""

    def test_pas_de_429_sans_fixture_actif(self, client):
        """10 requêtes consécutives sans le fixture → aucun 429."""
        for _ in range(10):
            response = client.post("/auth/login", json=PAYLOAD_LOGIN)
            assert response.status_code != 429
