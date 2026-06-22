"""Tests d'intégration pour le rate limiting (slowapi)."""

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

    def test_3_premieres_requetes_ne_sont_pas_bloquees(self, client, limiter_actif):
        for i in range(3):
            response = client.post("/api/generate", json=PAYLOAD_GENERATE)
            assert response.status_code != 429, (
                f"Requête {i + 1} bloquée trop tôt : {response.status_code}"
            )

    def test_4e_requete_retourne_429(self, client, limiter_actif):
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
