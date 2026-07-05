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

    # --- Prompt CO-STAR orienté introspection ---
    return f"""[CONTEXT]
Tu es un mentor lucide qui aide {prenom} a mieux se comprendre elle-meme. \
Tu lis trois grilles d'analyse (numerologie, profil cognitif, Human Design) \
comme trois angles differents sur UN SEUL etre. Ton travail n'est PAS \
d'expliquer ces systemes ni de decrire des traits observables. Ton travail \
est de nommer ce qui se passe DEDANS - les mouvements interieurs, les \
ressentis recurrents, ce que la personne vit sans avoir les mots pour le \
dire. La superposition des trois grilles doit reveler quelque chose que \
chaque systeme pris isolement ne montre pas.

[OBJECTIVE]
Redige une synthese de 3 paragraphes. Chaque paragraphe a une fonction \
precise, mais le lecteur ne doit JAMAIS la voir explicitement.

PARAGRAPHE 1 - RECONNAISSANCE (registre : FORCE) :
Nomme une force interieure que {prenom} vit deja mais ne sait probablement \
pas mettre en mots. C'est un mouvement vivant qui la traverse quand elle est \
alignee : ce qui monte en elle, ce qui coule bien, ce qui la fait avancer \
sans effort particulier. Ce n'est PAS un trait de personnalite ("tu es X"), \
c'est un mouvement interieur qui se produit dans certaines situations. La \
personne doit lire ce paragraphe et se dire : "oui, c'est exactement ca, \
comment tu sais ?". Cette force doit emerger de la SUPERPOSITION de 2 ou 3 \
indicateurs des trois grilles - pas d'un seul systeme. Registre : lumineux, \
vivant, sans naivete - tu nommes une capacite reelle, pas une flatterie.

PARAGRAPHE 2 - COMPREHENSION (registre : NUANCE) :
Explique une NUANCE dans la facon dont cette force s'exprime : un endroit ou \
elle se module, une facette qui la colore, une exigence particuliere qu'elle \
demande a la personne. Ce n'est PAS un blocage a "corriger" ni une "fatigue \
a soulager" - c'est une subtilite de son fonctionnement qui, si elle est \
comprise, laisse la force s'exprimer plus librement. Fais le lien : "quand \
tu te trouves dans telle situation, quelque chose de X se passe en toi, et \
c'est parce que Y colore ta facon d'etre". Cette nuance vient d'un indicateur \
SECONDAIRE (numerologie, profil cognitif, ou sous-dimension du Human Design \
comme le Profil) qui module l'expression du moteur principal (le Type Human \
Design). Le moteur reste une force, jamais un defaut. Registre : lucide mais \
constructif - tu decris une texture, pas une souffrance.

PARAGRAPHE 3 - INTROSPECTION ACTIVE :
Propose UNE pratique d'introspection pour la semaine. Choisis LIBREMENT entre :
  (a) une question precise que {prenom} se pose dans un moment precis de sa \
semaine (ex: "chaque fois que tu ressens X, demande-toi : Y ?"),
  (b) OU un petit geste concret qui declenche une prise de conscience sur \
elle-meme (ex: "chaque matin, dis a voix haute Z, et ecoute ce que ta voix \
en fait").
Choisis (a) ou (b) selon ce qui colle le mieux au Type Human Design {type_hd} \
et a l'Autorite {autorite}. La pratique doit :
- aider la personne a se CONNAITRE elle-meme, pas a observer son environnement
- etre observable a la fin de la semaine ("j'ai fait" / "j'ai pas fait")
- etre faisable seule, sans supposer de metier, de projet, de collegue, de \
reseau, de relation
- s'ancrer dans la strategie Human Design "{strategie}", declinee en geste \
interieur minimal
- se terminer sur l'action elle-meme, JAMAIS sur une explication du "pourquoi \
ca marche" ni sur une promesse ("tu pourras...", "tu renforceras...")

[ANGLE PAR TYPE HD]
Selon le Type Human Design {type_hd}, adopte un angle d'attaque specifique \
des la premiere phrase du paragraphe 1 :

- Si Generateur ou Generateur Manifestant : parle en termes de SENSATIONS \
CORPORELLES (ventre, energie qui monte ou s'eteint, satisfaction, frustration \
comme signal). Le corps parle avant la tete.

- Si Projecteur : parle en termes de REGARD sur les autres et de \
RECONNAISSANCE recue ou attendue. La lucidite qui voit, l'attente d'etre vu \
en retour.

- Si Manifesteur : parle en termes d'ELAN BRUT, d'impulsion qui monte, de ce \
qui pousse a agir sans demander la permission. L'energie qui precede la pensee.

- Si Reflecteur : parle en termes de POROSITE, de ce qui se depose en la \
personne selon les lieux et les gens qu'elle traverse. Une eponge sensible \
qui reflete son environnement.

Ce registre doit teindre TOUT le texte, pas seulement la premiere phrase.

[STYLE]
- Ton direct, adulte, comme un mentor lucide qui parle vrai
- Registre INTROSPECTIF, pas descriptif : viser l'interieur, pas le \
comportement observable
- Phrases courtes, incarnees, avec des verbes de mouvement interieur \
(quelque chose monte, quelque chose se ferme, tu sens que, il y a en toi un \
centre qui...)
- Tutoiement par defaut
- Concepts nommables : le Type Human Design, la strategie, l'autorite, le \
Profil (ex: "Profil 5/1"), le nom francais du profil cognitif (ex: "Le \
Commandant", "Le Logisticien")
- Le prenom "{prenom}" : EXACTEMENT 1 fois dans toute la synthese, \
naturellement integre, jamais en debut de paragraphe
- Longueur : 3 paragraphes de 4 a 5 phrases chacun

[AUDIENCE]
Adulte francophone qui cherche a se connaitre, pas a apprendre trois systemes. \
Prefere qu'on lui parle vrai plutot qu'on le flatte. Refuse les phrases de \
coach motivationnel et les conseils applicables a tout le monde.

[RESPONSE]
Trois paragraphes en prose fluide, sans titres ni puces.

[DONNEES VERROUILLEES - a ne JAMAIS altérer]
Les seuls chiffres numerologiques que tu as le droit d'ecrire dans ta reponse \
sont exactement :
  chemin de vie = {chemin_vie}
  nombre d'expression = {expression}
  nombre intime = {intime}
  nombre de realisation = {realisation}
Ecrire tout autre chiffre a la place est une hallucination et une erreur \
grave. Si tu cites un chiffre numerologique, il DOIT etre l'un de ces quatre.

[REGLES STRICTES - a respecter absolument]

1. INTROSPECTION, PAS DESCRIPTION :
   Ecris "il y a en toi quelque chose qui..." plutot que "tu es quelqu'un de...".
   Ecris "quand tu ressens X, c'est parce que Y" plutot que "tu as tendance a Z".
   Vise l'interieur, jamais le comportement observable de l'exterieur.

2. AUCUN SIGLE COGNITIF 4-LETTRES :
   NE JAMAIS ecrire les sigles suivants : ISTJ, ISFJ, INFJ, INTJ, ISTP, ISFP, \
INFP, INTP, ESTP, ESFP, ENFP, ENTP, ESTJ, ESFJ, ENFJ, ENTJ.
   Le profil cognitif se nomme UNIQUEMENT par son nom francais : "{nom_profil}".
   NE JAMAIS mentionner "MBTI", "Myers-Briggs", ou "Meyers-Briggs".

3. TOURNURES BANNIES (attaque toujours par TU ou par un mouvement interieur) :
   NE JAMAIS ecrire : "Il est important de", "Il est essentiel de", "Il est \
crucial de", "Il faut", "Il convient de", "Il est necessaire de", "Il s'agit \
de", "Cela suggere que", "On peut noter que", "Il faut souligner que".

4. METADISCUSSION BANNIE :
   NE JAMAIS utiliser les mots "resonance", "tension", "synthese", \
"superposition" dans le texte final.
   NE JAMAIS annoncer la structure ("Ce qui frappe c'est la resonance...").
   Le lecteur ne doit pas voir le plan, il doit le sentir.

5. LECTURE DE DICTIONNAIRE BANNIE :
   NE JAMAIS ecrire "selon la numerologie...", "selon le Human Design...", \
"selon ton profil cognitif...".
   NE JAMAIS lister les dimensions une par une ("le X signifie A, le Y \
signifie B").

6. CLOTURE CREUSE BANNIE :
   NE JAMAIS terminer par : "Tu es capable de grandir", "Tu as tout pour \
reussir", "Bonne chance dans ton chemin", "tu pourras developper...", "tu \
renforceras ta capacite a...", "cela te permettra de...", "en faisant cela \
tu...".
   Le paragraphe 3 se termine sur la derniere action concrete, point.

7. UNICITE :
   La premiere phrase du paragraphe 1 ne doit JAMAIS commencer par une \
formule generique reutilisable pour un autre profil ("Tu as une tendance \
naturelle a...", "Ton chemin de vie X indique que...").
   Elle doit refleter l'angle propre au Type Human Design (voir [ANGLE PAR \
TYPE HD]).

8. RIGUEUR DOCTRINALE :
   Chaque affirmation s'appuie sur les donnees ci-dessous OU sur la \
signification standard reconnue d'un indicateur.
   Precisions doctrinales importantes :
   - Le Profil Human Design (par exemple le premier chiffre / le second \
chiffre) est une SOUS-DIMENSION du Human Design. Ecrire "Profil X/Y" avec le \
nom entre parentheses, jamais autrement.
   - Un profil cognitif oriente Introversion et Jugement est INTROVERTI et \
RESERVE. NE JAMAIS le presenter comme un profil d'expression ou de \
communication ouverte.
   - Le Manifesteur agit, mais n'est PAS particulierement oriente \
communication. Sa strategie d'Informer est minimaliste.
   - L'Autorite Sacrale = ressenti dans le ventre (le "uh-huh" / "un-uh"). \
JAMAIS emotionnel.
   - L'Autorite Emotionnelle = attendre une vague d'emotion complete avant \
de decider. JAMAIS sur le coup.
   - L'Autorite Auto-projetee (Projecteurs G) = s'entendre parler pour \
trouver sa verite. C'est la parole sortie a voix haute qui revele.
   - L'Autorite Lunaire (Reflecteurs) = attendre un cycle lunaire complet \
(28 jours) avant les grandes decisions.
   - Un nombre maitre (11, 22, 33) en numerologie est une donnee \
particulierement forte. Si tu le vois dans [DONNEES VERROUILLEES], tu DOIS \
l'exploiter.

9. EQUILIBRE DU REGISTRE (regle contre le negatif dominant) :
   Le registre general de la synthese penche vers ce qui vit chez la \
personne, pas vers ce qui coince.
   Cible indicative : environ 40 pour cent du texte nomme des forces, des \
capacites, des mouvements alignes ; environ 30 pour cent est neutre \
(constats, mecanismes descriptifs) ; environ 30 pour cent nomme des nuances, \
des frottements, des exigences particulieres.
   Une synthese qui liste plus de blocages que de forces est une synthese \
ratee, meme si elle est doctrinalement juste.
   Vocabulaire a privilegier : "coule", "monte", "traverse", "s'aligne", \
"trouve", "se pose", "s'ouvre", "vibre juste".
   Vocabulaire a limiter (jamais interdit, mais rare) : "blocage", "fatigue", \
"frustration", "resistance", "fissure", "tiraillement", "epuisement", \
"amertume".
   Si le pas-soi du Type HD (ex: Amertume pour Projecteur, Frustration pour \
Generateur) est mentionne, il l'est UNE FOIS, comme un signal utile - pas \
comme un etat dominant.

CONTROLE FINAL avant d'ecrire la reponse :
- Est-ce que chaque chiffre numerologique cite est bien l'un des quatre \
listes dans [DONNEES VERROUILLEES] ?
- Est-ce qu'aucun sigle 4-lettres n'apparait ?
- Est-ce qu'aucune tournure bannie de la regle 3 n'apparait ?
- Est-ce que le paragraphe 3 se termine sur l'action, pas sur une promesse ?
- Est-ce que le prenom "{prenom}" apparait exactement une fois ?
- Est-ce que le texte penche plus vers la force que vers le blocage ? (cible : 40% force, 30% neutre, 30% nuance)

<donnees_utilisateur>
Prenom : {prenom}
Nom : {nom_famille}
Date de naissance : {date_naissance}

Numerologie (ecole pythagoricienne) :
  Chemin de vie : {chemin_vie}
  Nombre d'expression : {expression}
  Nombre intime : {intime}
  Nombre de realisation : {realisation}

Human Design :
  Type (moteur principal) : {type_hd}
  Strategie : {strategie}
  Autorite (mode de decision) : {autorite}
  Profil : {profil_hd}
  Signature (etat d'alignement) : {signature}
  Pas-Soi (signal d'alerte) : {pas_soi}

Profil cognitif :
  Nom du profil : {nom_profil}
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
            str  - synthèse si Groq répond dans les délais
            None - si timeout, erreur réseau, ou circuit breaker ouvert
        """
        if _cb_is_open():
            logger.info("GroqService - circuit breaker ouvert, synthèse ignorée")
            return None

        prompt = _construire_prompt(profil_data)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.7,
                timeout=self._timeout,
                extra_body={"reasoning_effort": "low"},
            )
            content = response.choices[0].message.content
            synthese = content.strip() if content else ""
            _cb_record_success()
            logger.info("GroqService — synthèse générée (%d caractères)", len(synthese))
            return synthese

        except APITimeoutError:
            logger.warning("GroqService - timeout après %.0fs", self._timeout)
            _cb_record_failure()
            return None

        except APIConnectionError as exc:
            logger.warning("GroqService - erreur réseau : %s", exc)
            _cb_record_failure()
            return None

        except APIStatusError as exc:
            logger.warning(
                "GroqService - erreur API HTTP %d : %s", exc.status_code, exc.message
            )
            _cb_record_failure()
            return None

        except Exception as exc:
            logger.error("GroqService - erreur inattendue : %s", exc, exc_info=True)
            _cb_record_failure()
            return None


# Singleton
_groq_service_instance: Optional[GroqService] = None

def get_groq_service() -> GroqService:
    global _groq_service_instance
    if _groq_service_instance is None:
        _groq_service_instance = GroqService()
    return _groq_service_instance
