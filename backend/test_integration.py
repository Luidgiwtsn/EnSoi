# backend/test_integration.py
from datetime import date, time
from app.services.human_design.ephemerides import calculer_double_carte
from app.services.human_design.gates import positions_vers_gates
from app.services.human_design.channels import calculer_canaux_actifs


def lancer_crash_test():
    print("====== CRASH-TEST INTEGRATION : HENRY DUPONT ======")

    date_naiss = date(2026, 1, 1)
    heure_naiss = time(12, 0)
    timezone = "Europe/London"

    print(f"\n[1] Calcul astronomique pour {date_naiss} a {heure_naiss} ({timezone})...")
    positions_astro = calculer_double_carte(date_naiss, heure_naiss, timezone)

    print("[2] Traduction des positions en Portes Rave...")
    gates_conscientes = positions_vers_gates(positions_astro["conscient"])
    gates_inconscientes = positions_vers_gates(positions_astro["inconscient"])

    toutes_les_gates = set()
    for p in gates_conscientes.values():
        toutes_les_gates.add(p["gate"])
    for p in gates_inconscientes.values():
        toutes_les_gates.add(p["gate"])

    print(f"-> Portes activees detectees ({len(toutes_les_gates)}): {sorted(toutes_les_gates)}")
    print(f"\n-> Detail gates conscientes (Personnalite): {gates_conscientes}")
    print(f"\n-> Detail gates inconscientes (Design): {gates_inconscientes}")

    print("\n[3] Analyse des correspondances de canaux via channels.py...")
    canaux_actifs = calculer_canaux_actifs(gates_conscientes, gates_inconscientes)

    print(f"\n-> CANAUX ACTIFS RECALCULES: {canaux_actifs}")
    print("\n-> ATTENDUS SUR LA CHARTE JOVIAN ARCHIVE (reference):")
    print("   - 10-20 (Awakening)")
    print("   - 35-36 (Transitoriness)")
    print("   - 37-40 (Community)")
    print("======================================================")


if __name__ == "__main__":
    lancer_crash_test()
