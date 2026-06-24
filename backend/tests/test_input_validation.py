"""
Tests d'intégration pour la validation des champs identité utilisateurs.

Vérifie que les contraintes Pydantic (pattern regex + max_length) refusent
les caractères non autorisés et les payloads géants, à la fois sur
/auth/register et sur /api/generate.
"""

import pytest


# ===================== /auth/register =====================


BASE_REGISTER = {
    "prenom": "Alice",
    "nom_famille": "Martin",
    "email": "validation@example.com",
    "password": "ValidPass1",
    "date_naissance": "1990-01-01",
}


def _payload_register(field: str, value, email_suffix: str = ""):
    """Construit un payload register avec un champ surchargé.

    Nettoie email_suffix des espaces et tirets pour générer un email RFC-valide
    même quand on teste des noms composés ("Du Pont" → "dupont").
    """
    safe_suffix = email_suffix.replace(" ", "").replace("-", "")
    return {
        **BASE_REGISTER,
        "email": f"validation{safe_suffix}@example.com",
        field: value,
    }


class TestRegisterPrenomValidation:
    """Validation du champ prenom à l'inscription."""

    @pytest.mark.parametrize("prenom", [
        "Alice",
        "Jean-Pierre",
        "Marie Claire",
        "François-Xavier",
        "Léa",
        "Mëlanie",
        "Anne-Sophie",
    ])
    def test_prenoms_valides_acceptes(self, client, prenom):
        """Les prénoms avec lettres, espaces, tirets et accents passent."""
        response = client.post(
            "/auth/register",
            json=_payload_register("prenom", prenom, email_suffix=prenom[:3].lower()),
        )
        assert response.status_code == 201, (
            f"Prénom valide rejeté : {prenom!r}"
        )

    @pytest.mark.parametrize("prenom", [
        "",                       # vide (min_length=1)
        "Alice123",               # chiffres interdits
        "Alice@Martin",           # @ interdit
        "Alice<script>",          # HTML interdit
        "Alice; DROP TABLE",      # injection SQL interdite
        "Alice\nMartin",          # newline interdit
        "👋 Alice",               # emojis interdits
        "Alice_Martin",           # underscore interdit
        "Alice.Martin",           # point interdit
        "A" * 101,                # trop long (max 100)
    ])
    def test_prenoms_invalides_rejetes(self, client, prenom):
        response = client.post(
            "/auth/register",
            json=_payload_register("prenom", prenom, email_suffix="invalid"),
        )
        assert response.status_code == 422, (
            f"Prénom invalide accepté : {prenom!r} → status {response.status_code}"
        )


class TestRegisterNomFamilleValidation:
    """Mêmes règles sur nom_famille."""

    @pytest.mark.parametrize("nom_famille", [
        "Martin",
        "Du Pont",
        "Saint-Laurent",
        "O Reilly",
    ])
    def test_noms_famille_valides(self, client, nom_famille):
        response = client.post(
            "/auth/register",
            json=_payload_register(
                "nom_famille", nom_famille, email_suffix=nom_famille[:3].lower()
            ),
        )
        assert response.status_code == 201

    @pytest.mark.parametrize("nom_famille", [
        "",
        "Martin1",
        "Martin@Dupont",
        "<img src=x>",
        "B" * 101,
    ])
    def test_noms_famille_invalides(self, client, nom_famille):
        response = client.post(
            "/auth/register",
            json=_payload_register("nom_famille", nom_famille, email_suffix="bad"),
        )
        assert response.status_code == 422


# ===================== /users/me (PATCH) =====================


class TestUpdateNomValidation:
    """Validation des champs prenom / nom_famille lors d'un PATCH /users/me."""

    @pytest.fixture
    def auth_headers(self, client):
        """Crée un utilisateur et retourne ses headers d'authentification."""
        client.post("/auth/register", json={
            "prenom": "Initial",
            "nom_famille": "User",
            "email": "update-test@example.com",
            "password": "ValidPass1",
            "date_naissance": "1990-01-01",
        })
        login = client.post("/auth/login", json={
            "email": "update-test@example.com",
            "password": "ValidPass1",
        })
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_update_prenom_valide(self, client, auth_headers):
        response = client.patch(
            "/users/me", json={"prenom": "Hélène"}, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["prenom"] == "Hélène"

    def test_update_nom_famille_valide(self, client, auth_headers):
        response = client.patch(
            "/users/me", json={"nom_famille": "De La Tour"}, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["nom_famille"] == "De La Tour"

    def test_update_les_deux_a_la_fois(self, client, auth_headers):
        response = client.patch(
            "/users/me",
            json={"prenom": "Jean-Marc", "nom_famille": "Dupond"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prenom"] == "Jean-Marc"
        assert data["nom_famille"] == "Dupond"

    @pytest.mark.parametrize("field,value", [
        ("prenom", "A" * 101),
        ("prenom", "Test123"),
        ("prenom", "<script>alert(1)</script>"),
        ("prenom", "x" * 50000),
        ("nom_famille", "B" * 101),
        ("nom_famille", "Martin@Dupond"),
    ])
    def test_update_valeurs_invalides_rejetees(
        self, client, auth_headers, field, value
    ):
        response = client.patch(
            "/users/me", json={field: value}, headers=auth_headers
        )
        assert response.status_code == 422, (
            f"{field}={value!r:.50} accepté → status {response.status_code}"
        )


# ===================== /api/generate =====================


class TestProfilRequestValidation:
    """
    Validation des champs prenom et nom_famille de POST /api/generate.

    Note : la validation regex existait déjà avant cette branche, ces tests
    sont une régression check pour s'assurer qu'elle reste active.
    """

    PAYLOAD_BASE = {
        "date_naissance": "1990-01-01",
        "reponses_cognitif": [3] * 12,
    }

    @pytest.mark.parametrize("field,value", [
        ("prenom", ""),
        ("prenom", "Alice123"),
        ("prenom", "Alice<script>"),
        ("prenom", "A" * 101),
        ("nom_famille", ""),
        ("nom_famille", "Martin@123"),
        ("nom_famille", "B" * 101),
    ])
    def test_caracteres_invalides_rejetes(self, client, field, value):
        payload = {
            **self.PAYLOAD_BASE,
            "prenom": "Alice",
            "nom_famille": "Martin",
            field: value,
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422
