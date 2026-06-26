"""Tests de la configuration CORS — verifie que le middleware accepte plusieurs origines.

Ces tests sont independants de la config .env : ils creent une mini-app FastAPI
avec une liste d'origines codee en dur, pour valider le comportement du middleware
CORSMiddleware quand on lui passe une liste d'origines.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient


def _build_app_with_origins(origins: list[str]) -> FastAPI:
    """Construit une mini-app FastAPI avec CORS configure pour les origines donnees."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/ping")
    def ping():
        return {"ok": True}

    return app


# App de test avec les 2 origines de developpement
app_test = _build_app_with_origins(
    ["http://localhost:5173", "http://127.0.0.1:5173"]
)
client = TestClient(app_test)


def test_cors_autorise_localhost_5173():
    """L'origine localhost:5173 recoit le header allow-origin."""
    response = client.options(
        "/ping",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_autorise_127_0_0_1_5173():
    """L'origine 127.0.0.1:5173 recoit le header allow-origin (fix principal)."""
    response = client.options(
        "/ping",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"


def test_cors_refuse_origine_non_autorisee():
    """Une origine non listee ne recoit PAS le header allow-origin."""
    response = client.options(
        "/ping",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "http://evil.example.com"
