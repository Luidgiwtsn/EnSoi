// Contenu pédagogique : Human Design
// Utilisé par le composant AboutSection et ValeurDetail.

export const humanDesignContenu = {
  titre: 'le Human Design',

  intro: {
    titre: "Qu'est-ce que le Human Design ?",
    paragraphes: [
      "Le Human Design est un système qui combine plusieurs traditions, astrologie, kabbale, chakras hindous, I Ching et physique quantique, pour proposer une lecture de votre fonctionnement énergétique. À partir de votre date, heure et lieu de naissance, il définit un type énergétique, une stratégie de décision et une autorité intérieure qui reflètent la manière dont vous êtes fait pour naviguer dans le monde.",
      "Il offre un cadre de compréhension riche pour mieux se connaître et s'aligner avec sa nature profonde.",
    ],
  },

  dimensions: {
    titre: 'Que signifient vos résultats ?',
    items: [
      {
        nom: 'Type énergétique',
        description:
          "Il décrit votre manière fondamentale d'utiliser et de partager votre énergie au quotidien. C'est la clé de voûte de votre profil.",
      },
      {
        nom: 'Stratégie',
        description:
          "Il s'agit de l'approche recommandée pour prendre des décisions et interagir avec votre environnement en cohérence avec votre type.",
      },
      {
        nom: 'Autorité intérieure',
        description:
          "C'est le mécanisme de décision propre à chacun : une boussole intérieure sur laquelle s'appuyer plutôt que sur le mental.",
      },
      {
        nom: 'Profil',
        description:
          "Deux chiffres qui décrivent la manière dont vous apprenez et interagissez avec les autres, entre exploration intérieure et engagement extérieur.",
      },
    ],
  },

  resultatsPersonnalises: {
    Manifesteur: {
      titre: 'Manifesteur',
      texte:
        "En tant que Manifesteur, vous êtes un initiateur naturel, capable de déclencher des projets et d'ouvrir la voie. Votre énergie fonctionne par impulsions puissantes suivies de temps de repos. Votre stratégie est d'informer votre entourage de vos intentions avant d'agir, pour limiter les résistances et préserver votre liberté d'action.",
    },
    'Générateur': {
      titre: 'Générateur',
      texte:
        "En tant que Générateur, vous disposez d'une énergie de vie puissante et durable, particulièrement lorsque vous êtes engagé dans une activité qui vous anime réellement. Votre stratégie est de répondre à ce qui se présente à vous plutôt que d'initier de force. Quand vous suivez ce qui vous met en joie, votre énergie devient contagieuse.",
    },
    'Générateur Manifestant': {
      titre: 'Générateur Manifestant',
      texte:
        "En tant que Générateur Manifestant, vous combinez l'énergie durable du Générateur avec la capacité d'initier du Manifestant. Vous fonctionnez souvent sur plusieurs projets à la fois, avec des sauts d'énergie rapides. Votre stratégie est de répondre puis d'informer votre entourage avant d'agir, pour fluidifier vos élans.",
    },
    Projecteur: {
      titre: 'Projecteur',
      texte:
        "En tant que Projecteur, vous êtes fait pour guider, conseiller et voir les autres avec justesse. Votre énergie est ciblée mais non continue : vous avez besoin de reconnaissance et d'invitations pour déployer votre potentiel. Votre stratégie est d'attendre l'invitation avant d'offrir votre vision, ce qui rend votre contribution reçue et valorisée.",
    },
    'Réflecteur': {
      titre: 'Réflecteur',
      texte:
        "En tant que Réflecteur, vous êtes un miroir de votre environnement, particulièrement sensible aux énergies collectives. Votre nature vous rend rare et précieux : vous percevez ce que les autres ne voient pas. Votre stratégie est d'attendre un cycle lunaire complet (28 jours) avant les décisions importantes, pour laisser la clarté émerger.",
    },
  },

  // NOUVEAU : détails par valeur cliquable (29 textes)
  // Sous-clé = nom de la dimension (type_hd, strategie, autorite, profil)
  detailsParValeur: {
    type_hd: {
      Manifesteur: {
        titre: 'Type · Manifesteur',
        texte:
          "Le Manifesteur est un initiateur naturel, capable de déclencher des projets et d'ouvrir la voie sans attendre. Son énergie fonctionne par impulsions puissantes suivies de temps de repos. Il représente environ 9% de la population.",
      },
      'Générateur': {
        titre: 'Type · Générateur',
        texte:
          "Le Générateur dispose d'une énergie de vie puissante et durable, particulièrement lorsqu'il est engagé dans une activité qui l'anime réellement. C'est le type le plus fréquent, environ 37% de la population, et le moteur énergétique du monde.",
      },
      'Générateur Manifestant': {
        titre: 'Type · Générateur Manifestant',
        texte:
          "Le Générateur Manifestant combine l'énergie durable du Générateur avec la capacité d'initier du Manifestant. Il fonctionne souvent sur plusieurs projets à la fois, avec des sauts d'énergie rapides. Environ 33% de la population.",
      },
      Projecteur: {
        titre: 'Type · Projecteur',
        texte:
          "Le Projecteur est fait pour guider, conseiller et voir les autres avec justesse. Son énergie n'est pas continue, il a besoin d'invitations et de reconnaissance pour déployer son potentiel. Environ 20% de la population.",
      },
      'Réflecteur': {
        titre: 'Type · Réflecteur',
        texte:
          "Le Réflecteur est un miroir de son environnement, particulièrement sensible aux énergies collectives. Sa nature le rend rare (environ 1% de la population) et précieux, capable de percevoir ce que les autres ne voient pas.",
      },
    },

    strategie: {
      "Informer avant d'agir": {
        titre: "Stratégie · Informer avant d'agir",
        texte:
          "Cette stratégie est celle du Manifesteur. Avant de lancer un projet ou de changer de direction, prévenir les personnes concernées désamorce les résistances et préserve votre liberté d'action. Ce n'est pas demander la permission, c'est offrir de la clarté.",
      },
      'Répondre à ce qui se présente': {
        titre: 'Stratégie · Répondre à ce qui se présente',
        texte:
          "Cette stratégie est celle du Générateur. Plutôt que d'initier de force, laissez la vie vous solliciter (une opportunité, une question, une situation) et écoutez la réponse viscérale de votre corps. Le \"oui\" intérieur ouvre la porte de l'énergie durable.",
      },
      'Répondre puis informer': {
        titre: 'Stratégie · Répondre puis informer',
        texte:
          "Cette stratégie combine celle du Générateur et celle du Manifestant. D'abord répondre à ce qui se présente (comme un Générateur), puis informer votre entourage avant d'agir (comme un Manifestant). Cela fluidifie vos élans rapides et évite les malentendus.",
      },
      "Attendre l'invitation": {
        titre: "Stratégie · Attendre l'invitation",
        texte:
          "Cette stratégie est celle du Projecteur. Pour les grands sujets (relation, travail, engagement), attendre d'être formellement invité rend votre contribution reçue et valorisée. Sans invitation, votre énergie de guidance peut se heurter à un mur.",
      },
      'Attendre un cycle lunaire (28 jours)': {
        titre: 'Stratégie · Attendre un cycle lunaire',
        texte:
          "Cette stratégie est celle du Réflecteur. Pour les décisions importantes, laisser passer un cycle lunaire complet permet à la clarté d'émerger progressivement, à mesure que vous ressentez la décision sous différentes énergies. La patience est votre alliée.",
      },
    },

    autorite: {
      'Émotionnelle (Plexus solaire)': {
        titre: 'Autorité · Émotionnelle',
        texte:
          "Votre boussole intérieure passe par la vague émotionnelle. Il n'y a pas de vérité dans l'instant : vos ressentis évoluent au fil des heures ou des jours, et la clarté vient d'avoir traversé plusieurs états. Attendre avant de décider est la clé.",
      },
      Sacrale: {
        titre: 'Autorité · Sacrale',
        texte:
          "Votre boussole intérieure est une réponse viscérale, dans le ventre. Face à une question ou une opportunité, un \"hum-hum\" (oui) ou \"hun-uh\" (non) monte spontanément. Cette réponse est immédiate, en dehors du mental, et rarement trompeuse.",
      },
      'Splénique': {
        titre: 'Autorité · Splénique',
        texte:
          "Votre boussole intérieure est une intuition instantanée, quasi silencieuse, qui parle une seule fois. Elle passe souvent par le corps (frisson, tension, détente) et disparaît si on ne l'écoute pas dans l'instant. C'est l'autorité du \"maintenant ou jamais\".",
      },
      'Ego (Cœur)': {
        titre: 'Autorité · Ego',
        texte:
          "Votre boussole intérieure vient de votre volonté et de votre désir profond. Décider selon ce que vous voulez vraiment (pas ce que vous devriez vouloir) et selon la juste mesure de votre énergie disponible est la voie de vos choix les plus alignés.",
      },
      'Auto-projetée (G)': {
        titre: 'Autorité · Auto-projetée',
        texte:
          "Votre boussole intérieure passe par la parole. Vous avez besoin d'entendre ce que vous pensez pour savoir ce que vous ressentez vraiment. Parler d'une décision à voix haute, à un ami de confiance ou même seul, révèle votre vérité intérieure.",
      },
      'Mentale (Projecteur mental)': {
        titre: 'Autorité · Mentale',
        texte:
          "Votre boussole intérieure ne passe pas par un centre unique mais par un dialogue avec votre environnement. Vous avez besoin d'échanger avec des personnes de confiance dans plusieurs lieux différents pour laisser émerger votre clarté.",
      },
      'Lunaire (Réflecteur)': {
        titre: 'Autorité · Lunaire',
        texte:
          "Votre boussole intérieure suit le cycle de la lune. Les décisions importantes se prennent après un cycle lunaire complet (28 jours), pendant lequel vous ressentez le sujet sous différentes énergies changeantes. Le temps est votre plus grand allié.",
      },
    },

    profil: {
      '1/3 - Investigateur / Martyr': {
        titre: 'Profil 1/3 · Investigateur / Martyr',
        texte:
          "La ligne 1 (Investigateur) explore consciemment les fondations, cherche à comprendre en profondeur avant d'agir. La ligne 3 (Martyr) apprend inconsciemment par essais et erreurs. Ce profil bâtit sa solidité en creusant les bases et en tirant les leçons de l'expérience.",
      },
      '1/4 - Investigateur / Opportuniste': {
        titre: 'Profil 1/4 · Investigateur / Opportuniste',
        texte:
          "La ligne 1 (Investigateur) cherche consciemment à maîtriser les fondations. La ligne 4 (Opportuniste) partage inconsciemment son savoir dans son réseau proche. Ce profil devient une ressource fiable pour son entourage grâce à la profondeur de ses connaissances.",
      },
      '2/4 - Ermite / Opportuniste': {
        titre: 'Profil 2/4 · Ermite / Opportuniste',
        texte:
          "La ligne 2 (Ermite) a besoin consciemment de solitude et de retrait pour se ressourcer. La ligne 4 (Opportuniste) tisse inconsciemment des liens et rayonne dans son réseau. Ce profil alterne entre bulle personnelle et vie sociale nourrissante.",
      },
      '2/5 - Ermite / Hérétique': {
        titre: 'Profil 2/5 · Ermite / Hérétique',
        texte:
          "La ligne 2 (Ermite) recherche consciemment le calme et la solitude. La ligne 5 (Hérétique) attire inconsciemment des projections des autres, appelé à apporter des solutions pratiques. Ce profil est souvent sollicité malgré lui pour son expertise.",
      },
      '3/5 - Martyr / Hérétique': {
        titre: 'Profil 3/5 · Martyr / Hérétique',
        texte:
          "La ligne 3 (Martyr) apprend consciemment par l'expérience et les erreurs. La ligne 5 (Hérétique) attire inconsciemment les projections et les demandes d'aide. Ce profil apporte des solutions concrètes forgées dans le vécu.",
      },
      '3/6 - Martyr / Modèle': {
        titre: 'Profil 3/6 · Martyr / Modèle',
        texte:
          "La ligne 3 (Martyr) apprend consciemment par l'expérimentation. La ligne 6 (Modèle) passe inconsciemment par trois phases de vie : expérimentation jusqu'à ~30 ans, retrait et observation jusqu'à ~50 ans, puis sagesse partagée. Ce profil devient sage par le vécu.",
      },
      '4/6 - Opportuniste / Modèle': {
        titre: 'Profil 4/6 · Opportuniste / Modèle',
        texte:
          "La ligne 4 (Opportuniste) tisse consciemment des liens forts dans son réseau. La ligne 6 (Modèle) traverse inconsciemment les trois phases de vie et devient un exemple. Ce profil incarne au fil du temps ce qu'il partage avec ses proches.",
      },
      '4/1 - Opportuniste / Investigateur': {
        titre: 'Profil 4/1 · Opportuniste / Investigateur',
        texte:
          "La ligne 4 (Opportuniste) rayonne consciemment dans son cercle. La ligne 1 (Investigateur) creuse inconsciemment les fondations et cherche à comprendre. Ce profil est influent auprès des siens grâce à des connaissances solides accumulées en profondeur.",
      },
      '5/1 - Hérétique / Investigateur': {
        titre: 'Profil 5/1 · Hérétique / Investigateur',
        texte:
          "La ligne 5 (Hérétique) attire consciemment les projections des autres et est appelée à proposer des solutions. La ligne 1 (Investigateur) creuse inconsciemment les bases. Ce profil apporte des réponses pratiques ancrées dans une compréhension solide.",
      },
      '5/2 - Hérétique / Ermite': {
        titre: 'Profil 5/2 · Hérétique / Ermite',
        texte:
          "La ligne 5 (Hérétique) attire consciemment les projections et les sollicitations. La ligne 2 (Ermite) a inconsciemment besoin de retrait pour se ressourcer. Ce profil oscille entre exposition publique et besoin fort de recul.",
      },
      '6/2 - Modèle / Ermite': {
        titre: 'Profil 6/2 · Modèle / Ermite',
        texte:
          "La ligne 6 (Modèle) traverse consciemment les trois phases de vie. La ligne 2 (Ermite) a inconsciemment besoin de solitude pour retrouver son essence. Ce profil devient une figure d'inspiration après un long parcours d'apprentissage et de retrait.",
      },
      '6/3 - Modèle / Martyr': {
        titre: 'Profil 6/3 · Modèle / Martyr',
        texte:
          "La ligne 6 (Modèle) traverse consciemment les trois phases de vie. La ligne 3 (Martyr) apprend inconsciemment par l'expérimentation. Ce profil devient sage à travers de nombreuses expériences, souvent tumultueuses dans la première partie de vie.",
      },
    },
  },
};

export function getResultatHumanDesign(typeHd) {
  return humanDesignContenu.resultatsPersonnalises[typeHd] || null;
}

// NOUVEAU : renvoie le détail pour une valeur individuelle du HD.
// dimension : 'type_hd' | 'strategie' | 'autorite' | 'profil'
// Ex: getDetailHumanDesign('strategie', "Attendre l'invitation") → { titre, texte }
export function getDetailHumanDesign(dimension, valeur) {
  const dimData = humanDesignContenu.detailsParValeur[dimension];
  if (!dimData) return null;
  return dimData[valeur] || null;
}
