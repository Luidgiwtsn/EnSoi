"""Tests d'integration - POST /api/profils/{id}/share et GET /public/{token}.

Couvre :
- Creation de lien de partage (proprietaire uniquement)
- Acces public via token (synthese IA exclue cote securite)
- Gestion des erreurs (token inexistant, 401, 403)
"""
from unittest.mock import MagicMock, patch


# Payload reutilisable pour creer un profil
PAYLOAD_VALIDE = {
    "prenom": "Alice",
    "nom_famille": "Martin",
    "date_naissance": "1990-06-12",
    "reponses_cognitif": [3, 2, 4, 1, 5, 2, 3, 4, 1, 5, 2, 3],
}


# Helpers
def _register_and_login(
    client,
    email: str = "alice@test.com",
    prenom: str = "Alice",
) -> str:
    """Inscrit un utilisateur et retourne son access_token."""
    client.post("/auth/register", json={
        "prenom": prenom,
        "nom_famille": "Test",
        "email": email,
        "password": "Secret123!",
        "date_naissance": "1990-06-12",
    })
    resp = client.post("/auth/login", json={
        "email": email,
        "password": "Secret123!",
    })
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_profil(client, headers: dict) -> int:
    """Cree un profil avec Groq mocke et retourne son id."""
    with patch("app.routers.profils.GroqService") as mock_cls:
        mock_cls.return_value.generer_synthese = MagicMock(
            return_value="Synthese personnelle confidentielle."
        )
        response = client.post("/api/generate", json=PAYLOAD_VALIDE, headers=headers)
    return response.json()["id"]


# POST /api/profils/{id}/share - creation de lien
class TestCreateShareToken:

    def test_proprietaire_peut_creer_un_lien(self, client):
        """Le proprietaire d'un profil peut creer un lien de partage."""
        token = _register_and_login(client)
        headers = _auth_headers(token)
        profil_id = _create_profil(client, headers)

        response = client.post(f"/api/profils/{profil_id}/share", headers=headers)

        assert response.status_code == 201
        body = response.json()
        assert "url" in body
        assert "token" in body
        assert "expires_at" in body
        assert body["url"].endswith(f"/public/{body['token']}")

    def test_non_proprietaire_recoit_403(self, client):
        """Un utilisateur autre que le proprietaire ne peut pas creer de lien."""
        token1 = _register_and_login(client, email="alice@test.com", prenom="Alice")
        profil_id = _create_profil(client, _auth_headers(token1))

        token2 = _register_and_login(client, email="bob@test.com", prenom="Bob")
        response = client.post(
            f"/api/profils/{profil_id}/share",
            headers=_auth_headers(token2),
        )

        assert response.status_code == 403

    def test_sans_token_refuse_la_requete(self, client):
        """Sans token JWT, l'endpoint refuse la requete (401 ou 403)."""
        response = client.post("/api/profils/1/share")
        assert response.status_code in (401, 403)


# GET /public/{token} - acces public
class TestGetProfilPublic:

    def test_acces_avec_token_valide_retourne_profil(self, client):
        """Avec un token valide, on recoit le profil complet (sauf synthese)."""
        token = _register_and_login(client)
        headers = _auth_headers(token)
        profil_id = _create_profil(client, headers)

        share_response = client.post(f"/api/profils/{profil_id}/share", headers=headers)
        share_token = share_response.json()["token"]

        response = client.get(f"/public/{share_token}")

        assert response.status_code == 200
        body = response.json()
        assert body["prenom"] == "Alice"
        assert body["nom_famille"] == "Martin"
        assert "numerologie" in body
        assert "profil_cognitif" in body
        assert "human_design" in body

    def test_synthese_ia_absente_de_la_reponse_publique(self, client):
        """SECURITE : la synthese IA ne doit JAMAIS etre exposee via /public/{token}.

        Verrouille le response_model_exclude={'synthese_ia'} sur l'endpoint.
        Si quelqu'un retire cette option, ce test echoue immediatement.
        """
        token = _register_and_login(client)
        headers = _auth_headers(token)
        profil_id = _create_profil(client, headers)

        share_response = client.post(f"/api/profils/{profil_id}/share", headers=headers)
        share_token = share_response.json()["token"]

        response = client.get(f"/public/{share_token}")

        assert response.status_code == 200
        body = response.json()
        assert "synthese_ia" not in body, (
            "FAILLE SECURITE : synthese_ia est exposee dans la reponse publique. "
            "Verifier response_model_exclude sur GET /public/{token}."
        )

    def test_token_inexistant_retourne_404(self, client):
        """Un token qui n'existe pas en BDD retourne 404."""
        response = client.get("/public/token-qui-nexiste-pas")
        assert response.status_code == 404
