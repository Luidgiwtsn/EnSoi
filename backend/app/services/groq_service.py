# backend/app/services/groq_service.py

import logging
import time
from typing import Optional

from groq import Groq, APITimeoutError, APIConnectionError, APIStatusError

from app.config import settings

logger = logging.getLogger(__name__)


# Circuit breaker — état partagé au niveau du module (singleton de processus)

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
Tu es un guide de développement personnel bienveillant et perspicace. \
Tu aides les gens à mieux se comprendre grâce à une lecture intégrée de plusieurs systèmes \
(numérologie, profil cognitif, Human Design).

[OBJECTIVE]
Rédige une synthèse personnalisée et encourageante pour {prenom}, \
en croisant les trois systèmes ci-dessous. \
La synthèse doit aider {prenom} à comprendre ses forces, son mode de fonctionnement naturel, \
et une piste concrète d'action.

[STYLE]
- Ton chaleureux, direct, sans jargon ésotérique excessif
- Français courant, phrases courtes
- Personnalisé : utilise le prénom "{prenom}" au moins deux fois
- Pas de liste à puces — uniquement des paragraphes fluides
- Longueur : 3 paragraphes de 4 à 6 phrases chacun

[AUDIENCE]
Adulte francophone curieux de mieux se connaître, ouvert mais pas initié \
aux systèmes ésotériques.

[RESPONSE]
Trois paragraphes :
1. Qui tu es — portrait croisé des trois systèmes
2. Comment tu fonctionnes — mode d'action naturel et décision
3. Ta piste — une action concrète et personnalisée pour cette période

<donnees_utilisateur>
Prénom : {prenom}
Nom : {nom_famille}
Date de naissance : {date_naissance}

Numérologie :
  Chemin de vie : {chemin_vie}
  Nombre d'expression : {expression}
  Nombre intime : {intime}
  Nombre de réalisation : {realisation}

Human Design :
  Type : {type_hd}
  Stratégie : {strategie}
  Autorité : {autorite}
  Profil : {profil_hd}

Profil cognitif :
  Type : {type_cognitif} — {nom_profil}
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
        self._client = Groq(api_key=settings.GROQ_API_KEY)
        self._model = settings.GROQ_MODEL
        self._timeout = float(settings.GROQ_TIMEOUT)

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
groq_service = GroqService()
