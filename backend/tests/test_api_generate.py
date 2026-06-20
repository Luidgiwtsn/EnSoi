"""Tests d'intégration — POST /generate et endpoints /profils."""
from unittest.mock import MagicMock, patch

import pytest


# Payload de base réutilisable

PAYLOAD_VALIDE = {
    "prenom": "Alice",
    "nom_famille": "Martin",
    "date_naissance": "1990-06-12",
    "reponses_cognitif": [3, 2, 4, 1, 5, 2, 3, 4, 1, 5, 2, 3],
}



# Helpers


def _register_and_login(client) -> str:
    """
    Inscrit un utilisateur de test et retourne son access_token.
    Utilisé pour les endpoints protégés (GET /profils, DELETE, etc.)
    """
    client.post("/auth/register", json={
        "nom": "Alice Test",
        "email": "alice@test.com",
        "password": "Secret123!",
        "date_naissance": "1990-06-12",
    })
    resp = client.post("/auth/login", json={
        "email": "alice@test.com",
        "password": "Secret123!",
    })
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}



# POST /generate - cas nominaux


class TestGenerateNominaux:

    def test_generate_retourne_200(self, client):
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value="Synthèse test.")
            response = client.post("/generate", json=PAYLOAD_VALIDE)
        assert response.status_code == 200

    def test_generate_retourne_profil_complet(self, client):
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value="Synthèse test.")
            response = client.post("/generate", json=PAYLOAD_VALIDE)
        data = response.json()
        assert "numerologie" in data
        assert "human_design" in data
        assert "profil_cognitif" in data
        assert "synthese_ia" in data

    def test_generate_statut_complet_si_groq_ok(self, client):
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value="Synthèse test.")
            response = client.post("/generate", json=PAYLOAD_VALIDE)
        assert response.json()["statut"] == "complet"

    def test_generate_statut_partiel_si_groq_indisponible(self, client):
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value=None)
            response = client.post("/generate", json=PAYLOAD_VALIDE)
        data = response.json()
        assert data["statut"] == "partiel"
        assert data["synthese_ia"] is None

    def test_generate_avec_heure_et_lieu(self, client):
        payload = {**PAYLOAD_VALIDE, "heure_naissance": "14:30:00", "lieu_naissance": "Paris"}
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value="Synthèse.")
            response = client.post("/generate", json=payload)
        assert response.status_code == 200



# POST /generate - cas d'erreur (422)


class TestGenerateErreurs:

    def test_prenom_vide_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "prenom": ""}
        response = client.post("/generate", json=payload)
        assert response.status_code == 422

    def test_date_future_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "date_naissance": "2099-01-01"}
        response = client.post("/generate", json=payload)
        assert response.status_code == 422

    def test_reponses_manquantes_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "reponses_cognitif": [1, 2, 3]}
        response = client.post("/generate", json=payload)
        assert response.status_code == 422

    def test_reponse_hors_range_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "reponses_cognitif": [0, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2]}
        response = client.post("/generate", json=payload)
        assert response.status_code == 422

    def test_date_malformee_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "date_naissance": "not-a-date"}
        response = client.post("/generate", json=payload)
        assert response.status_code == 422



# GET /profils et GET /profils/{id}


class TestGetProfils:

    def test_get_profils_retourne_liste(self, client):
        token = _register_and_login(client)
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value=None)
            client.post("/generate", json=PAYLOAD_VALIDE, headers=_auth_headers(token))
        response = client.get("/profils", headers=_auth_headers(token))
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

    def test_get_profil_par_id(self, client):
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value=None)
            profil_id = client.post("/generate", json=PAYLOAD_VALIDE).json()["id"]
        response = client.get(f"/profils/{profil_id}")
        assert response.status_code == 200
        assert response.json()["id"] == profil_id

    def test_get_profil_inexistant_retourne_404(self, client):
        response = client.get("/profils/99999")
        assert response.status_code == 404

    def test_get_profils_sans_token_retourne_401(self, client):
        response = client.get("/profils")
        assert response.status_code == 403



# DELETE /profils/{id}


class TestDeleteProfil:

    def test_delete_profil_retourne_200(self, client):
        token = _register_and_login(client)
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value=None)
            profil_id = client.post(
                "/generate", json=PAYLOAD_VALIDE, headers=_auth_headers(token)
            ).json()["id"]
        response = client.delete(f"/profils/{profil_id}", headers=_auth_headers(token))
        assert response.status_code == 200

    def test_delete_profil_supprime_de_la_bdd(self, client):
        token = _register_and_login(client)
        with patch("app.routers.profils.GroqService") as mock_cls:
            mock_cls.return_value.generer_synthese = MagicMock(return_value=None)
            profil_id = client.post(
                "/generate", json=PAYLOAD_VALIDE, headers=_auth_headers(token)
            ).json()["id"]
        client.delete(f"/profils/{profil_id}", headers=_auth_headers(token))
        response = client.get(f"/profils/{profil_id}")
        assert response.status_code == 404

    def test_delete_profil_inexistant_retourne_404(self, client):
        token = _register_and_login(client)
        response = client.delete("/profils/99999", headers=_auth_headers(token))
        assert response.status_code == 404

    def test_delete_profil_sans_token_retourne_401(self, client):
        response = client.delete("/profils/1")
        assert response.status_code == 403



# GET /api/health


class TestHealth:

    def test_health_retourne_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["database"] == "ok"
