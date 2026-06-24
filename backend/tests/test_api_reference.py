"""
Tests d'intégration pour les endpoints de référence (/api/countries,
/api/timezones).

Ces endpoints servent les listes statiques utilisées par le frontend
pour peupler les <select> du formulaire de génération de profil.
On teste le contrat HTTP (format, statut, tri) — pas la justesse de
pycountry/pytz/Babel qui sont des bibliothèques tierces.
"""


def test_countries_returns_200(client):
    """L'endpoint countries doit répondre 200 sans authentification."""
    response = client.get("/api/countries")
    assert response.status_code == 200


def test_countries_format(client):
    """
    Le format attendu est {"countries": [{"code": str, "name": str}, ...]}
    avec code alpha-2 (2 caractères).
    """
    response = client.get("/api/countries")
    data = response.json()

    assert "countries" in data
    assert isinstance(data["countries"], list)
    assert len(data["countries"]) > 200  # pycountry en liste ~250

    premier = data["countries"][0]
    assert set(premier.keys()) == {"code", "name"}
    assert len(premier["code"]) == 2
    assert premier["code"].isupper()
    assert isinstance(premier["name"], str)
    assert len(premier["name"]) > 0


def test_countries_contains_france_in_french(client):
    """
    Vérifie que Babel a bien traduit en français : la France apparaît avec
    le nom "France" (et non "France" anglais — qui est identique, mais on
    teste aussi l'Allemagne pour être sûr).
    """
    response = client.get("/api/countries")
    countries = response.json()["countries"]

    by_code = {c["code"]: c["name"] for c in countries}
    assert by_code.get("FR") == "France"
    assert by_code.get("DE") == "Allemagne"  # Germany en anglais
    assert by_code.get("ES") == "Espagne"    # Spain en anglais


def test_countries_sorted_alphabetically(client):
    """La liste doit être triée par nom pour un affichage <select> propre."""
    response = client.get("/api/countries")
    countries = response.json()["countries"]
    noms = [c["name"] for c in countries]
    assert noms == sorted(noms)


def test_timezones_returns_200_and_format(client):
    """
    L'endpoint timezones doit répondre 200 et renvoyer
    {"timezones": [str, ...]} avec des identifiants IANA (contiennent un "/").
    """
    response = client.get("/api/timezones")
    assert response.status_code == 200

    data = response.json()
    assert "timezones" in data
    assert isinstance(data["timezones"], list)
    assert len(data["timezones"]) > 400  # pytz.all_timezones ~590

    # Tous les fuseaux IANA suivent le format "Région/Ville"
    # sauf quelques exceptions historiques (UTC, GMT, etc.)
    fuseaux_avec_slash = [tz for tz in data["timezones"] if "/" in tz]
    assert len(fuseaux_avec_slash) > 400


def test_timezones_contains_known_zones_and_sorted(client):
    """
    Vérifie la présence de fuseaux connus et le tri alphabétique.
    Cohérence avec pytz.all_timezones côté validation backend.
    """
    response = client.get("/api/timezones")
    timezones = response.json()["timezones"]

    assert "Europe/Paris" in timezones
    assert "America/New_York" in timezones
    assert "Asia/Tokyo" in timezones
    assert "UTC" in timezones

    assert timezones == sorted(timezones)
