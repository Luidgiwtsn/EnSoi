"""Service Profil Cognitif — 12 questions, 4 axes, curseur 1-5."""

from typing import List, Tuple


# --- Questions ---

QUESTIONS = [
    # Axe Énergie (I/E)
    {
        "id": 1, "axe": "energie",
        "texte": "Pour recharger vos batteries après une semaine intense, vous avez plutôt besoin de...",
        "pole_a": "Moments de calme et de tranquillité dans votre bulle",
        "pole_b": "Changements d'air et d'interactions avec l'extérieur",
    },
    {
        "id": 2, "axe": "energie",
        "texte": "Dans une discussion de groupe, vous vous situez généralement comme...",
        "pole_a": "Observateur attentif, vous parlez quand c'est nécessaire",
        "pole_b": "Animateur naturel, vous alimentez facilement l'échange",
    },
    {
        "id": 3, "axe": "energie",
        "texte": "Après avoir passé beaucoup de temps au milieu de la foule, vous vous sentez...",
        "pole_a": "Vidé de votre énergie, vous devez vous isoler pour récupérer",
        "pole_b": "Stimulé et dynamique, cela vous a donné de l'élan",
    },
    # Axe Perception (N/S)
    {
        "id": 4, "axe": "perception",
        "texte": "Face à un nouveau projet ou sujet d'apprentissage, vous préférez...",
        "pole_a": "Explorer les théories, les liens cachés et imaginer le futur",
        "pole_b": "Savoir tout de suite comment ça marche et l'appliquer concrètement",
    },
    {
        "id": 5, "axe": "perception",
        "texte": "Pour vous faire une opinion sur une situation, vous vous fiez d'abord à...",
        "pole_a": "Votre intuition globale et vos ressentis immédiats",
        "pole_b": "Des éléments tangibles, des faits vérifiables et précis",
    },
    {
        "id": 6, "axe": "perception",
        "texte": "Dans votre façon de voir les choses, vous êtes plutôt attiré par...",
        "pole_a": "Le potentiel d'une idée et ce qui pourrait advenir",
        "pole_b": "La réalité du moment présent et ce qui existe déjà",
    },
    # Axe Décision (F/T)
    {
        "id": 7, "axe": "decision",
        "texte": "Lorsqu'un désaccord survient dans votre entourage, votre réflexe est de...",
        "pole_a": "Prendre soin de l'état émotionnel de chacun pour apaiser le groupe",
        "pole_b": "Analyser objectivement la situation pour trouver la cause réelle",
    },
    {
        "id": 8, "axe": "decision",
        "texte": "Si vous devez guider ou conseiller un proche en difficulté, vous privilégiez...",
        "pole_a": "L'écoute bienveillante, le soutien et l'encouragement",
        "pole_b": "Le recul critique, la vérité constructive et les solutions",
    },
    {
        "id": 9, "axe": "decision",
        "texte": "Pour vous, une décision juste se prend principalement avec...",
        "pole_a": "Le cœur, en accord avec vos valeurs personnelles et humaines",
        "pole_b": "La tête, en toute impartialité et de manière logique",
    },
    # Axe Organisation (J/P)
    {
        "id": 10, "axe": "organisation",
        "texte": "Pour vos journées de repos ou vos vacances, vous préférez...",
        "pole_a": "Avoir un fil conducteur clair pour savoir à quoi s'attendre",
        "pole_b": "Décider au jour le jour selon vos envies du moment",
    },
    {
        "id": 11, "axe": "organisation",
        "texte": "Face à une tâche importante qui vous est confiée, vous avez tendance à...",
        "pole_a": "Créer une structure à l'avance pour avancer régulièrement et sereinement",
        "pole_b": "Attendre le bon élan d'énergie pour la réaliser d'un coup, quitte à être dans l'urgence",
    },
    {
        "id": 12, "axe": "organisation",
        "texte": "Si un changement de plan de dernière minute bouscule votre programme, vous...",
        "pole_a": "Ressentez un inconfort, vous préférez quand les choses sont d'équerre",
        "pole_b": "Rebondissez facilement, vous aimez l'imprévu et l'adaptabilité",
    },
]

# --- 16 types ---

TYPES_COGNITIFS = {
    "INTJ": "L'Architecte",   "INTP": "Le Logicien",
    "ENTJ": "Le Commandant",  "ENTP": "Le Débatteur",
    "INFJ": "Le Protecteur",  "INFP": "Le Médiateur",
    "ENFJ": "Le Protagoniste","ENFP": "L'Inspirateur",
    "ISTJ": "Le Logisticien", "ISFJ": "Le Défenseur",
    "ESTJ": "Le Directeur",   "ESFJ": "Le Consul",
    "ISTP": "Le Virtuose",    "ISFP": "L'Aventurier",
    "ESTP": "L'Entrepreneur", "ESFP": "L'Animateur",
}

NOMS_DIMENSIONS = {
    "energie":      {"a": "Introversion", "b": "Extraversion"},
    "perception":   {"a": "Intuition",    "b": "Sensation"},
    "decision":     {"a": "Sentiment",    "b": "Logique"},
    "organisation": {"a": "Jugement",     "b": "Perception"},
}

LETTRES_AXES = {
    "energie":      {"a": "I", "b": "E"},
    "perception":   {"a": "N", "b": "S"},
    "decision":     {"a": "F", "b": "T"},
    "organisation": {"a": "J", "b": "P"},
}


def _analyser_axe(reponses: List[int]) -> Tuple[str, int]:
    """
    Analyse un axe à partir de 3 réponses (curseur 1-5).
    Score min=3 (3x1), max=15 (3x5).
    Retourne le pôle dominant et son pourcentage d'ancrage.
    """
    total = sum(reponses)
    pourcentage_b = round(((total - 3) / (15 - 3)) * 100)

    if pourcentage_b > 50:
        return "b", pourcentage_b
    elif pourcentage_b < 50:
        return "a", (100 - pourcentage_b)
    else:
        return "a", 51  # égalité → pôle A par défaut, 51% pour cohérence visuelle


def calculer(reponses: List[int]) -> dict:
    """
    Calcule le profil cognitif à partir de 12 réponses (curseur 1-5).
    Retourne type_cognitif, nom_profil et dimensions avec pourcentages.
    """
    if len(reponses) != 12:
        raise ValueError(f"12 réponses attendues, {len(reponses)} reçues")
    if not all(1 <= r <= 5 for r in reponses):
        raise ValueError("Chaque réponse doit être entre 1 et 5")

    axes = {
        "energie":      reponses[0:3],
        "perception":   reponses[3:6],
        "decision":     reponses[6:9],
        "organisation": reponses[9:12],
    }

    resultats = {axe: _analyser_axe(vals) for axe, vals in axes.items()}

    type_cognitif = "".join(
        LETTRES_AXES[axe][pole]
        for axe, (pole, _) in resultats.items()
    )

    return {
        "type_cognitif": type_cognitif,
        "nom_profil": TYPES_COGNITIFS[type_cognitif],
        "dimensions": {
            axe: {
                "dominant": NOMS_DIMENSIONS[axe][pole],
                "lettre": LETTRES_AXES[axe][pole],
                "score_pourcentage": score,
            }
            for axe, (pole, score) in resultats.items()
        }
    }


def get_questions() -> List[dict]:
    """Retourne les 12 questions pour le frontend."""
    return QUESTIONS
