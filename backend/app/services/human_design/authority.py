# backend/app/services/human_design/authority.py
"""
Détermination de l'Autorité Intérieure Human Design.

L'Autorité Intérieure est la méthode de prise de décision propre à
chaque personne. Elle dépend d'une HIÉRARCHIE STRICTE des centres
définis : un seul centre prime à la fois, dans l'ordre suivant :

1. Solar Plexus (Émotionnelle)    - la plus prioritaire
2. Sacral (Sacrale)
3. Spleen (Splénique)
4. Heart (Ego / Cœur)
5. G Center (Auto-projetée / Self-Projected) - Projecteurs uniquement
6. Mentale (Projecteurs sans aucun des centres ci-dessus)
7. Lunaire (Réflecteurs : aucun centre défini)

VALIDATION EMPIRIQUE EFFECTUEE (juin 2026) :
Hiérarchie confirmée par plusieurs sources indépendantes :
- humdes.com/kb/authority/ (référence francophone)
- Jovian Archive (référence officielle)
- freehumandesignchart.com
- wholeandunleashed.com
- Human Design Collective

Aucune divergence entre les sources sur l'ordre de priorité.

Cas de référence Henry Dupont (Solar Plexus défini) :
- Autorité attendue : Émotionnelle (Plexus solaire)
- Charte officielle Jovian Archive : "Inner Authority: Solar Plexus" ✓
"""
from typing import List, Tuple
from app.services.human_design.centers import calculer_centres_definis


# Les 7 Autorités du Human Design (noms français)
AUTORITES = {
    "EMOTIONNELLE": "Émotionnelle (Plexus solaire)",
    "SACRALE": "Sacrale",
    "SPLENIQUE": "Splénique",
    "EGO": "Ego (Cœur)",
    "AUTO_PROJETEE": "Auto-projetée (G)",
    "MENTALE": "Mentale (Projecteur mental)",
    "LUNAIRE": "Lunaire (Réflecteur)",
}


def determiner_autorite(canaux_actifs: List[Tuple[int, int]]) -> str:
    """
    Détermine l'Autorité Intérieure selon la hiérarchie standard.

    Applique l'ordre de priorité : Solar Plexus > Sacral > Spleen > Heart
    > G (auto-projetée) > Mentale > Lunaire.

    Seul le centre le plus prioritaire compte : un Générateur avec Solar
    Plexus ET Sacral définis aura une Autorité Émotionnelle, pas Sacrale.
    """
    centres_definis = calculer_centres_definis(canaux_actifs)

    # Cas spécial : Réflecteur (aucun centre défini)
    if len(centres_definis) == 0:
        return AUTORITES["LUNAIRE"]

    # Hiérarchie stricte
    if "solar_plexus" in centres_definis:
        return AUTORITES["EMOTIONNELLE"]
    if "sacral" in centres_definis:
        return AUTORITES["SACRALE"]
    if "spleen" in centres_definis:
        return AUTORITES["SPLENIQUE"]
    if "heart" in centres_definis:
        return AUTORITES["EGO"]
    if "g" in centres_definis:
        return AUTORITES["AUTO_PROJETEE"]

    # Aucun des centres "d'autorité" n'est défini, mais d'autres centres
    # le sont (Throat, Head, Ajna, Root). C'est le cas du Projecteur Mental.
    return AUTORITES["MENTALE"]
