# backend/app/services/groq_service.py

import logging
import time
from typing import Optional

from groq import Groq, APITimeoutError, APIConnectionError, APIStatusError

from app.config import settings

logger = logging.getLogger(__name__)


# Circuit breaker - état partagé au niveau du module (singleton de processus)

_cb_failures: int = 0
_cb_opened_at: Optional[float] = None
_CB_THRESHOLD = 3
_CB_RECOVERY_SEC = 60


def _cb_is_open() -> bool:
    global _cb_opened_at
    if _cb_opened_at is None:
        return False
    if time.monotonic() - _cb_opened_at >= _CB_RECOVERY_SEC:
        return False  # half-open : on laisse passer un essai
    return True


def _cb_record_success() -> None:
    global _cb_failures, _cb_opened_at
    _cb_failures = 0
    _cb_opened_at = None


def _cb_record_failure() -> None:
    global _cb_failures, _cb_opened_at
    _cb_failures += 1
    if _cb_failures >= _CB_THRESHOLD:
        _cb_opened_at = time.monotonic()
        logger.warning(
            "GroqService — circuit breaker OUVERT après %d échecs consécutifs",
            _cb_failures,
        )



# Prompt CO-STAR


def _sanitize(value: str, max_len: int = 100) -> str:
    """Supprime les sauts de ligne et tronque — défense en profondeur
    contre l'injection dans la partie instructions du prompt.
    La validation Pydantic en amont (pattern alphanumérique) est la
    première ligne de défense ; ceci est le filet de sécurité."""
    return str(value)[:max_len].replace("\n", " ").replace("\r", " ")


def _construire_prompt(profil_data: dict) -> str:
    """
    Construit le prompt CO-STAR.
    Les données utilisateur sont isolées dans <donnees_utilisateur> pour
    signaler au modèle qu'elles constituent des données, pas des instructions.
    """
    # --- Extraction et sanitization ---
    prenom = _sanitize(profil_data.get("prenom", ""))
    nom_famille = _sanitize(profil_data.get("nom_famille", ""))
    date_naissance = _sanitize(profil_data.get("date_naissance", ""), max_len=10)

    num = profil_data.get("numerologie", {})
    chemin_vie = int(num.get("chemin_vie", 0))
    expression = int(num.get("expression", 0))
    intime = int(num.get("intime", 0))
    realisation = int(num.get("realisation", 0))

    hd = profil_data.get("human_design", {})
    type_hd = _sanitize(hd.get("type_hd", ""), max_len=50)
    strategie = _sanitize(hd.get("strategie", ""))
    autorite = _sanitize(hd.get("autorite", ""))
    profil_hd = _sanitize(hd.get("profil", ""), max_len=50)
    signature = _sanitize(hd.get("signature", ""), max_len=50)
    pas_soi = _sanitize(hd.get("pas_soi", ""), max_len=50)

    cognitif = profil_data.get("profil_cognitif", {})
    nom_profil = _sanitize(cognitif.get("nom_profil", ""))
    type_cognitif = _sanitize(cognitif.get("type_cognitif", ""), max_len=10)

    # Extraction correcte des dimensions imbriquées
    dimensions = cognitif.get("dimensions", {})
    dims_list = []
    for axe, data_axe in dimensions.items():
        if isinstance(data_axe, dict):
            score = data_axe.get("score_pourcentage", 50)
            dominant = data_axe.get("dominant", "")
            dims_list.append(f"{axe} ({dominant}): {score}%")
    dims_str = ", ".join(dims_list[:4])

    # --- Prompt CO-STAR ---
    return f"""[CONTEXT]
Tu es un mentor lucide qui lit trois grilles d'analyse (numérologie, profil cognitif, \
Human Design) comme trois angles complémentaires sur LA MÊME personne. Ton travail \
n'est pas d'expliquer chaque système, mais de montrer ce qui se révèle quand on les \
superpose.

[OBJECTIVE]
Rédige une synthèse de 3 paragraphes pour {prenom}. Chaque paragraphe a une fonction \
précise, mais le lecteur ne doit JAMAIS la voir explicitement :
- Paragraphe 1 : repère 2 ou 3 indicateurs des 3 systèmes qui pointent dans la même \
direction. Décris ce qu'ils disent ENSEMBLE, comme une seule force.
- Paragraphe 2 : repère un indicateur SECONDAIRE qui résiste ou complique le moteur \
principal décrit au § 1. Explore franchement ce qui coince.
- Paragraphe 3 : propose UNE micro-pratique pour la semaine, applicable IMMÉDIATEMENT \
sans rien savoir d'autre sur la personne. Ni son métier, ni ses projets en cours, ni \
ses relations - tu ne sais RIEN de tout ça, donc ne suppose RIEN.
La pratique doit être :
(a) observable : on peut dire à la fin de la semaine "j'ai fait" ou "j'ai pas fait" ;
(b) faisable seule, dans n'importe quelle vie quotidienne (pas de "appelle un \
collègue", pas de "envoie un message à ton réseau") ;
(c) ancrée dans la stratégie Human Design ({strategie}) : c'est cette stratégie qui \
EST la pratique, déclinée en geste minimal.

Exemples du bon niveau :
- Manifesteur (Informer) : "Cette semaine, avant chaque décision qui touche quelqu'un \
d'autre (même petite : 'je sors ce soir', 'je passe à autre chose'), prends 5 secondes \
pour la dire à voix haute à la personne concernée avant de la faire. C'est ton geste \
d'Informer, ramené à l'échelle d'une semaine."
- Générateur (Répondre) : "Cette semaine, observe quelles propositions, demandes, \
sollicitations te font réagir avec un OUI franc dans le ventre - pas dans la tête. \
Note-les dans ton téléphone. À la fin de la semaine, regarde le motif."
- Projecteur (Attendre l'invitation) : "Cette semaine, pour les choses qui te tentent, \
ne propose pas - laisse les autres venir vers toi. Compte combien de fois ça arrive \
naturellement quand tu cesses de pousser."

L'action ne doit JAMAIS supposer un projet, un réseau, un collègue, un emploi.

[STYLE]
- Ton direct et adulte, comme un mentor lucide qui dit ce qu'il voit
- Phrases courtes et concrètes, verbes d'action
- Tutoiement par défaut
- Pas de jargon ésotérique, mais les concepts peuvent être nommés (Manifesteur, chemin \
de vie 3, Autorité Émotionnelle)
- Le prénom "{prenom}" : 1 à 2 fois maximum dans toute la synthèse
- Longueur : 3 paragraphes de 4 à 5 phrases chacun

[AUDIENCE]
Adulte francophone curieux, ouvert mais pas initié. Préfère qu'on lui parle vrai plutôt \
qu'on le flatte. N'aime ni les phrases de coach motivationnel, ni les conseils \
applicables à tout le monde.

[RESPONSE]
Trois paragraphes en prose fluide, sans titres ni puces.

À NE PAS FAIRE (règles strictes) :

1. Tournures impersonnelles BANNIES (règle stricte, contrôlée à la fin) :
   Ne JAMAIS écrire "Il est important de", "Il est essentiel de", "Il faut", \
"Il convient de", "Cela suggère que", "On peut noter que", "Il faut souligner que", \
"Il est nécessaire de", "Il est crucial de", "Il s'agit de".
   Avant de valider chaque paragraphe, RELIS-LE et remplace toute phrase qui \
commence par "Il" suivi du verbe être par une phrase directe avec "tu".
   Exemple : "Il est important de trouver un équilibre" → "Trouve un équilibre".

2. Métadiscussion BANNIE :
   Ne JAMAIS utiliser les mots "résonance", "tension", "synthèse" dans le texte.
   Ne JAMAIS annoncer la structure ("La résonance entre les systèmes est frappante", \
"Il y a une tension notable"). Le lecteur ne doit pas voir le plan, il doit le sentir.

3. Lecture de dictionnaire BANNIE :
   Ne JAMAIS écrire "selon la numérologie/le Human Design/ton profil cognitif, tu \
es...".
   Ne JAMAIS lister les dimensions une par une ("le 3 signifie X, le 7 signifie Y").

4. Diagnostic cohérent OBLIGATOIRE :
   Le Type Human Design est le MOTEUR PRINCIPAL de la personne. C'est une force, \
jamais un défaut à contenir.
   Si tu identifies une tension au § 2, elle vient d'une dimension SECONDAIRE qui \
complique l'expression de ce moteur, pas du moteur lui-même.
   Ne JAMAIS présenter le même indicateur comme une force au § 1 puis comme un \
problème au § 2.

5. Conseils génériques BANNIS :
   Ne JAMAIS conseiller "prendre du recul", "méditer", "faire du sport", "créer un \
espace calme", "réfléchir à tes objectifs", "écouter ton intuition".
   L'action du § 3 doit être : (a) un verbe précis, (b) un objet précis, (c) une \
échéance précise. Exemple : "Lundi, envoie un message à [type de personne précis] \
pour lui dire [contenu précis]".

6. Clôture creuse BANNIE :
   Ne JAMAIS terminer par "Tu es capable de grandir", "Tu as tout pour réussir", \
"Bonne chance dans ton chemin".
   Terminer sur la dernière action concrète, point.

7. Prénom :
   Ne JAMAIS commencer un paragraphe par le prénom.
   Le prénom "{prenom}" doit apparaître EXACTEMENT 1 fois dans la synthèse, naturellement \
intégré dans une phrase, idéalement au milieu du § 2 ou au début du § 3 pour ancrer un \
moment important.

8. Rigueur doctrinale OBLIGATOIRE (règle anti-broderie) :
   Tu ne dois affirmer QUE des choses directement étayées par les données envoyées \
ci-dessous OU par la signification standard reconnue d'un indicateur (numérologie \
pythagoricienne, Human Design selon Jovian Archive, profil cognitif).
   Si tu hésites sur la justesse d'un croisement, tu PRÉFÈRES ne pas le faire plutôt \
que d'inventer un lien plausible.

   Règles de précision factuelle :
   - Le Profil 2/4 (Ermite / Opportuniste) est une SOUS-DIMENSION du Human Design, \
ne JAMAIS écrire "Ermite/Opportuniste en Human Design", écrire "Profil 2/4 \
(Ermite / Opportuniste)".
   - Un profil cognitif orienté Introversion et Jugement est un profil INTROVERTI et RÉSERVÉ. Ne JAMAIS \
le présenter comme un profil d'expression ou de communication ouverte.
   - Le Manifesteur agit, mais n'est PAS particulièrement orienté communication. Sa \
stratégie d'Informer est minimaliste : il prévient les personnes affectées par ses \
décisions, ce n'est pas du dialogue.
   - Le Nombre d'expression 7 signifie ANALYSE, PROFONDEUR, RECHERCHE. Ne JAMAIS \
en déduire une "peur de communiquer" ou un "doute en soi", ce n'est pas son champ.
   - L'Autorité Émotionnelle signifie : attendre une vague d'émotion complète avant \
de décider (jamais "sur le coup"). Si tu mobilises ce concept, sois précis.

   Test final avant de produire :
   - Chaque affirmation peut être justifiée par les données ci-dessous OU par un \
ouvrage de référence reconnu.
   - Aucun croisement n'est inventé pour produire une narration fluide.
   - Aucune dimension du profil n'est attribuée à un autre système.

<donnees_utilisateur>
Prénom : {prenom}
Nom : {nom_famille}
Date de naissance : {date_naissance}

Numérologie (école pythagoricienne) :
  Chemin de vie : {chemin_vie}
  Nombre d'expression : {expression}
  Nombre intime : {intime}
  Nombre de réalisation : {realisation}

Human Design :
  Type (moteur principal) : {type_hd}
  Stratégie : {strategie}
  Autorité (mode de décision) : {autorite}
  Profil : {profil_hd}
  Signature (état d'alignement) : {signature}
  Pas-Soi (signal d'alerte) : {pas_soi}

Profil cognitif (4 axes) :
  Code : {type_cognitif} ({nom_profil})
  Dimensions : {dims_str}
</donnees_utilisateur>"""



# Service principal


class GroqService:
    """
    Encapsule les appels à l'API Groq avec :
    - timeout configurable (GROQ_TIMEOUT, défaut 8s)
    - circuit breaker (3 échecs → ouverture 60s, half-open auto)
    - retour None si indisponible → statut='partiel' côté appelant
    """

    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model
        self._timeout = float(settings.groq_timeout)

    def generer_synthese(self, profil_data: dict) -> Optional[str]:
        """
        Returns:
            str  — synthèse si Groq répond dans les délais
            None — si timeout, erreur réseau, ou circuit breaker ouvert
        """
        if _cb_is_open():
            logger.info("GroqService — circuit breaker ouvert, synthèse ignorée")
            return None

        prompt = _construire_prompt(profil_data)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7,
                timeout=self._timeout,
            )
            synthese = response.choices[0].message.content.strip()
            _cb_record_success()
            logger.info("GroqService — synthèse générée (%d caractères)", len(synthese))
            return synthese

        except APITimeoutError:
            logger.warning("GroqService — timeout après %.0fs", self._timeout)
            _cb_record_failure()
            return None

        except APIConnectionError as exc:
            logger.warning("GroqService — erreur réseau : %s", exc)
            _cb_record_failure()
            return None

        except APIStatusError as exc:
            logger.warning(
                "GroqService — erreur API HTTP %d : %s", exc.status_code, exc.message
            )
            _cb_record_failure()
            return None

        except Exception as exc:
            logger.error("GroqService — erreur inattendue : %s", exc, exc_info=True)
            _cb_record_failure()
            return None


# Singleton
_groq_service_instance: Optional[GroqService] = None

def get_groq_service() -> GroqService:
    global _groq_service_instance
    if _groq_service_instance is None:
        _groq_service_instance = GroqService()
    return _groq_service_instance
