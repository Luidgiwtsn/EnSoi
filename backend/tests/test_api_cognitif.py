"""Tests d'intégration pour GET /api/cognitif/questions."""

AXES_VALIDES = {"energie", "perception", "decision", "organisation"}


def test_get_questions_returns_200(client):
    """L'endpoint doit retourner 200 avec une liste de questions."""
    response = client.get("/api/cognitif/questions")
    assert response.status_code == 200


def test_get_questions_no_auth_required(client):
    """L'endpoint est public : aucun token requis."""
    response = client.get("/api/cognitif/questions")
    assert response.status_code == 200
    # Vérifie qu'aucun WWW-Authenticate n'est demandé
    assert "WWW-Authenticate" not in response.headers


def test_get_questions_returns_exactly_12(client):
    """Le questionnaire doit contenir exactement 12 questions."""
    response = client.get("/api/cognitif/questions")
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) == 12


def test_get_questions_structure_complete(client):
    """Chaque question doit avoir id, axe, texte, pole_a, pole_b."""
    response = client.get("/api/cognitif/questions")
    questions = response.json()["questions"]

    for q in questions:
        assert set(q.keys()) >= {"id", "axe", "texte", "pole_a", "pole_b"}
        assert isinstance(q["id"], int)
        assert isinstance(q["texte"], str) and len(q["texte"]) > 0
        assert isinstance(q["pole_a"], str) and len(q["pole_a"]) > 0
        assert isinstance(q["pole_b"], str) and len(q["pole_b"]) > 0
        assert q["axe"] in AXES_VALIDES


def test_get_questions_3_per_axis(client):
    """Chaque axe doit avoir exactement 3 questions (12 / 4 = 3)."""
    response = client.get("/api/cognitif/questions")
    questions = response.json()["questions"]

    counts = {axe: 0 for axe in AXES_VALIDES}
    for q in questions:
        counts[q["axe"]] += 1

    for axe, count in counts.items():
        assert count == 3, f"L'axe '{axe}' doit avoir 3 questions, trouvé {count}"


def test_get_questions_ids_unique_and_sequential(client):
    """Les IDs doivent être uniques et aller de 1 à 12."""
    response = client.get("/api/cognitif/questions")
    questions = response.json()["questions"]

    ids = [q["id"] for q in questions]
    assert sorted(ids) == list(range(1, 13))
