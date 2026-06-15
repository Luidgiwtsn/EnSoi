"""Tests intégration - router auth JWT."""
import pytest
from fastapi.testclient import TestClient


# Helpers


VALID_USER = {
    "nom": "Alice Martin",
    "email": "alice@ensoi.fr",
    "password": "Motdepasse1",
    "date_naissance": "1990-06-12",
}


def register(client: TestClient, data: dict = None) -> dict:
    """Inscrit un utilisateur et retourne la réponse JSON."""
    return client.post("/auth/register", json=data or VALID_USER).json()


def login(client: TestClient, email: str = None, password: str = None) -> dict:
    """Connecte un utilisateur et retourne la réponse JSON."""
    return client.post("/auth/login", json={
        "email": email or VALID_USER["email"],
        "password": password or VALID_USER["password"],
    }).json()


def auth_headers(client: TestClient) -> dict:
    """Inscrit, connecte et retourne les headers Bearer pour les tests protégés."""
    client.post("/auth/register", json=VALID_USER)
    tokens = login(client)
    return {"Authorization": f"Bearer {tokens['access_token']}"}



# POST /auth/register


def test_register_succes(client: TestClient):
    """Inscription valide → 201 + access_token + refresh_token."""
    response = client.post("/auth/register", json=VALID_USER)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_email_duplique(client: TestClient):
    """Même email deux fois → 409."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post("/auth/register", json=VALID_USER)
    assert response.status_code == 409
    assert "existe déjà" in response.json()["detail"]


def test_register_mdp_trop_court(client: TestClient):
    """MDP < 8 caractères → 400."""
    data = {**VALID_USER, "email": "test2@ensoi.fr", "password": "Ab1"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "8 caractères" in response.json()["detail"]


def test_register_mdp_sans_majuscule(client: TestClient):
    """MDP sans majuscule → 400."""
    data = {**VALID_USER, "email": "test3@ensoi.fr", "password": "motdepasse1"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "majuscule" in response.json()["detail"]


def test_register_mdp_sans_chiffre(client: TestClient):
    """MDP sans chiffre → 400."""
    data = {**VALID_USER, "email": "test4@ensoi.fr", "password": "Motdepasse"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "chiffre" in response.json()["detail"]


def test_register_email_invalide(client: TestClient):
    """Email mal formé → 422 (validation Pydantic)."""
    data = {**VALID_USER, "email": "pas-un-email"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 422


def test_register_champs_manquants(client: TestClient):
    """Body incomplet → 422."""
    response = client.post("/auth/register", json={"email": "x@x.fr"})
    assert response.status_code == 422



# POST /auth/login


def test_login_succes(client: TestClient):
    """Login valide → 200 + tokens."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post("/auth/login", json={
        "email": VALID_USER["email"],
        "password": VALID_USER["password"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_mauvais_mot_de_passe(client: TestClient):
    """Mauvais MDP → 401 avec message générique."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post("/auth/login", json={
        "email": VALID_USER["email"],
        "password": "MauvaisMotDePasse1",
    })
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"]


def test_login_email_inconnu(client: TestClient):
    """Email inexistant → 401 avec même message générique (anti user-enumeration)."""
    response = client.post("/auth/login", json={
        "email": "inconnu@ensoi.fr",
        "password": "Motdepasse1",
    })
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"]


def test_login_email_normalise(client: TestClient):
    """Login avec email en majuscules → 200 (normalisation lowercase)."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post("/auth/login", json={
        "email": "ALICE@ENSOI.FR",
        "password": VALID_USER["password"],
    })
    assert response.status_code == 200



# POST /auth/refresh


def test_refresh_succes(client: TestClient):
    """Refresh token valide → 200 + nouveau couple de tokens."""
    client.post("/auth/register", json=VALID_USER)
    tokens = login(client)
    response = client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    # Le refresh token est aléatoire → toujours différent
    assert new_tokens["refresh_token"] != tokens["refresh_token"]
    # Note : access_token peut être identique si login+refresh < 1s (même exp JWT)


def test_refresh_rotation_ancien_token_invalide(client: TestClient):
    """Après rotation, l'ancien refresh token → 401."""
    client.post("/auth/register", json=VALID_USER)
    tokens = login(client)
    old_refresh = tokens["refresh_token"]
    # Utiliser le token une première fois
    client.post("/auth/refresh", json={"refresh_token": old_refresh})
    # Réutiliser l'ancien → doit échouer
    response = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert response.status_code == 401
    assert "révoqué" in response.json()["detail"]


def test_refresh_token_invalide(client: TestClient):
    """Token aléatoire → 401."""
    response = client.post("/auth/refresh", json={
        "refresh_token": "token_bidon_qui_nexiste_pas"
    })
    assert response.status_code == 401



# POST /auth/logout


def test_logout_succes(client: TestClient):
    """Logout avec token valide → 200."""
    headers = auth_headers(client)
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200
    assert "réussie" in response.json()["message"]


def test_logout_refresh_token_revoque(client: TestClient):
    """Après logout, le refresh token ne fonctionne plus."""
    client.post("/auth/register", json=VALID_USER)
    tokens = login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    # Logout
    client.post("/auth/logout", headers=headers)
    # Tenter un refresh → doit échouer
    response = client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert response.status_code == 401


def test_logout_sans_token(client: TestClient):
    """Logout sans Authorization header → 403."""
    response = client.post("/auth/logout")
    assert response.status_code == 403



# POST /auth/change-password


def test_change_password_succes(client: TestClient):
    """Changement MDP valide → 200."""
    headers = auth_headers(client)
    response = client.post("/auth/change-password", headers=headers, json={
        "current_password": VALID_USER["password"],
        "new_password": "NouveauMdp2",
    })
    assert response.status_code == 200
    assert "succès" in response.json()["message"]


def test_change_password_ancien_mdp_incorrect(client: TestClient):
    """Mauvais MDP actuel → 401."""
    headers = auth_headers(client)
    response = client.post("/auth/change-password", headers=headers, json={
        "current_password": "MauvaisAncien1",
        "new_password": "NouveauMdp2",
    })
    assert response.status_code == 401


def test_change_password_nouveau_mdp_invalide(client: TestClient):
    """Nouveau MDP sans majuscule → 400."""
    headers = auth_headers(client)
    response = client.post("/auth/change-password", headers=headers, json={
        "current_password": VALID_USER["password"],
        "new_password": "sansmajuscule1",
    })
    assert response.status_code == 400


def test_change_password_invalide_refresh_token(client: TestClient):
    """Après change-password, l'ancien refresh token est révoqué."""
    client.post("/auth/register", json=VALID_USER)
    tokens = login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    # Changer le MDP
    client.post("/auth/change-password", headers=headers, json={
        "current_password": VALID_USER["password"],
        "new_password": "NouveauMdp2",
    })
    # L'ancien refresh token ne doit plus fonctionner
    response = client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert response.status_code == 401


def test_change_password_puis_login_nouveau_mdp(client: TestClient):
    """Après change-password, connexion avec le nouveau MDP → 200."""
    headers = auth_headers(client)
    client.post("/auth/change-password", headers=headers, json={
        "current_password": VALID_USER["password"],
        "new_password": "NouveauMdp2",
    })
    response = client.post("/auth/login", json={
        "email": VALID_USER["email"],
        "password": "NouveauMdp2",
    })
    assert response.status_code == 200


def test_change_password_sans_token(client: TestClient):
    """Sans Authorization header → 403."""
    response = client.post("/auth/change-password", json={
        "current_password": VALID_USER["password"],
        "new_password": "NouveauMdp2",
    })
    assert response.status_code == 403
