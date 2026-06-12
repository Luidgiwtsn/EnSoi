"""Tests d'intégration — POST /api/generate et endpoints /api/profils."""
from unittest.mock import patch

import pytest



# Payload de base réutilisable

PAYLOAD_VALIDE = {
    "prenom": "Alice",
    "nom_famille": "Martin",
    "date_naissance": "1990-06-12",
    "reponses_cognitif": [3, 2, 4, 1, 5, 2, 3, 4, 1, 5, 2, 3],
}



# POST /api/generate - cas nominaux


class TestGenerateNominaux:

    def test_generate_retourne_201(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = "Synthèse test."
            response = client.post("/api/generate", json=PAYLOAD_VALIDE)
        assert response.status_code == 201

    def test_generate_retourne_profil_complet(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = "Synthèse test."
            response = client.post("/api/generate", json=PAYLOAD_VALIDE)
        data = response.json()
        assert "numerologie" in data
        assert "human_design" in data
        assert "profil_cognitif" in data
        assert "synthese_ia" in data

    def test_generate_statut_complet_si_groq_ok(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = "Synthèse test."
            response = client.post("/api/generate", json=PAYLOAD_VALIDE)
        assert response.json()["statut"] == "complet"

    def test_generate_statut_partiel_si_groq_indisponible(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = None
            response = client.post("/api/generate", json=PAYLOAD_VALIDE)
        data = response.json()
        assert data["statut"] == "partiel"
        assert data["synthese_ia"] is None

    def test_generate_avec_heure_et_lieu(self, client):
        payload = {**PAYLOAD_VALIDE, "heure_naissance": "14:30:00", "lieu_naissance": "Paris"}
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = "Synthèse."
            response = client.post("/api/generate", json=payload)
        assert response.status_code == 201



# POST /api/generate — cas d'erreur (422)

class TestGenerateErreurs:

    def test_prenom_vide_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "prenom": ""}
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422

    def test_date_future_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "date_naissance": "2099-01-01"}
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422

    def test_reponses_manquantes_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "reponses_cognitif": [1, 2, 3]}
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422

    def test_reponse_hors_range_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "reponses_cognitif": [0, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2]}
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422

    def test_date_malformee_retourne_422(self, client):
        payload = {**PAYLOAD_VALIDE, "date_naissance": "not-a-date"}
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422



# GET /api/profils et GET /api/profils/{id}


class TestGetProfils:

    def test_get_profils_retourne_liste(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = None
            client.post("/api/generate", json=PAYLOAD_VALIDE)
        response = client.get("/api/profils")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

    def test_get_profil_par_id(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = None
            profil_id = client.post("/api/generate", json=PAYLOAD_VALIDE).json()["id"]
        response = client.get(f"/api/profils/{profil_id}")
        assert response.status_code == 200
        assert response.json()["id"] == profil_id

    def test_get_profil_inexistant_retourne_404(self, client):
        response = client.get("/api/profils/99999")
        assert response.status_code == 404



# DELETE /api/profils/{id}


class TestDeleteProfil:

    def test_delete_profil_retourne_200(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = None
            profil_id = client.post("/api/generate", json=PAYLOAD_VALIDE).json()["id"]
        response = client.delete(f"/api/profils/{profil_id}")
        assert response.status_code == 200

    def test_delete_profil_supprime_de_la_bdd(self, client):
        with patch("app.routers.profils.get_groq_service") as mock_groq:
            mock_groq.return_value.generer_synthese.return_value = None
            profil_id = client.post("/api/generate", json=PAYLOAD_VALIDE).json()["id"]
        client.delete(f"/api/profils/{profil_id}")
        response = client.get(f"/api/profils/{profil_id}")
        assert response.status_code == 404

    def test_delete_profil_inexistant_retourne_404(self, client):
        response = client.delete("/api/profils/99999")
        assert response.status_code == 404



# GET /api/health#

class TestHealth:

    def test_health_retourne_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["database"] == "ok"
