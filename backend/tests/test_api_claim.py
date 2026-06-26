"""Tests d'integration - POST /api/profils/{id}/claim."""
from unittest.mock import MagicMock, patch


# Payloads de test


PAYLOAD_PROFIL = {
    "prenom": "Test",
    "nom_famille": "Anonyme",
    "date_naissance": "1990-01-01",
    "reponses_cognitif": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
}

USER_A = {
    "prenom": "Alice",
    "nom_famille": "Martin",
    "email": "alice@test.com",
    "password": "Secret123!",
    "date_naissance": "1990-06-12",
}

USER_B = {
    "prenom": "Bob",
    "nom_famille": "Dupont",
    "email": "bob@test.com",
    "password": "Secret123!",
    "date_naissance": "1992-03-20",
}


# Helpers


def _register_and_login(client, user_data: dict) -> str:
    """Inscrit un utilisateur et retourne son access_token."""
    client.post("/auth/register", json=user_data)
    resp = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"],
    })
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _generate_profil_anonyme(client) -> dict:
    """
    Genere un profil anonyme (sans header Authorization) et retourne le JSON.
    Groq est mocke pour eviter les appels API reels.
    """
    with patch("app.routers.profils.GroqService") as mock_cls:
        mock_cls.return_value.generer_synthese = MagicMock(return_value="Synthese test.")
        resp = client.post("/api/generate", json=PAYLOAD_PROFIL)
    assert resp.status_code == 200, f"Generation profil echouee: {resp.json()}"
    return resp.json()


# Tests


class TestClaimEndpoint:

    def test_claim_success(self, client):
        """Claim avec bon token: 200, claim_token efface, profil rattache."""
        token = _register_and_login(client, USER_A)
        profil = _generate_profil_anonyme(client)

        # Sanity check : le profil anonyme a bien un claim_token
        assert profil["claim_token"] is not None

        resp = client.post(
            f"/api/profils/{profil['id']}/claim",
            json={"claim_token": profil["claim_token"]},
            headers=_auth_headers(token),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == profil["id"]
        assert body["claim_token"] is None  # token efface apres usage

    def test_claim_conflict_already_claimed(self, client):
        """Re-claim sur un profil deja rattache: 409."""
        token = _register_and_login(client, USER_A)
        profil = _generate_profil_anonyme(client)

        # Premier claim (succes)
        client.post(
            f"/api/profils/{profil['id']}/claim",
            json={"claim_token": profil["claim_token"]},
            headers=_auth_headers(token),
        )

        # Second claim sur le meme profil
        resp = client.post(
            f"/api/profils/{profil['id']}/claim",
            json={"claim_token": profil["claim_token"]},
            headers=_auth_headers(token),
        )

        assert resp.status_code == 409
        assert "deja rattache" in resp.json()["detail"]

    def test_claim_invalid_token(self, client):
        """Claim avec un token bidon sur profil anonyme: 403."""
        token = _register_and_login(client, USER_A)
        profil = _generate_profil_anonyme(client)

        resp = client.post(
            f"/api/profils/{profil['id']}/claim",
            json={"claim_token": "00000000-0000-0000-0000-000000000000"},
            headers=_auth_headers(token),
        )

        assert resp.status_code == 403
        assert "invalide" in resp.json()["detail"]

    def test_claim_without_auth(self, client):
        """Claim sans header Authorization: 403 (Starlette default sur HTTPBearer absent)."""
        profil = _generate_profil_anonyme(client)

        resp = client.post(
            f"/api/profils/{profil['id']}/claim",
            json={"claim_token": profil["claim_token"]},
        )

        # FastAPI/Starlette renvoie 403 quand HTTPBearer est absent, pas 401.
        # 401 est reserve aux tokens presents mais invalides (expires, malformes).
        assert resp.status_code == 403

    def test_claim_nonexistent_profil(self, client):
        """Claim sur un id inexistant: 404."""
        token = _register_and_login(client, USER_A)

        resp = client.post(
            "/api/profils/99999/claim",
            json={"claim_token": "00000000-0000-0000-0000-000000000000"},
            headers=_auth_headers(token),
        )

        assert resp.status_code == 404
        assert "introuvable" in resp.json()["detail"]

    def test_claim_token_is_one_shot(self, client):
        """
        Apres un claim reussi, le token est efface. Un autre utilisateur ne peut
        pas revendiquer le meme profil avec l'ancien token (409 car deja rattache).
        Verifie la propriete one-shot de bout en bout.
        """
        token_a = _register_and_login(client, USER_A)
        profil = _generate_profil_anonyme(client)
        original_claim_token = profil["claim_token"]

        # User A claim le profil
        resp1 = client.post(
            f"/api/profils/{profil['id']}/claim",
            json={"claim_token": original_claim_token},
            headers=_auth_headers(token_a),
        )
        assert resp1.status_code == 200

        # User B tente de claim le meme profil avec le meme token
        token_b = _register_and_login(client, USER_B)
        resp2 = client.post(
            f"/api/profils/{profil['id']}/claim",
            json={"claim_token": original_claim_token},
            headers=_auth_headers(token_b),
        )
        assert resp2.status_code == 409  # deja rattache, pas 403 (test important)
