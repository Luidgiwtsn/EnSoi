// Contenu pédagogique : Profil Cognitif
// Utilisé par le composant AboutSection et ValeurDetail.

export const profilCognitifContenu = {
  titre: 'le profil cognitif',

  intro: {
    titre: "Qu'est-ce que le profil cognitif ?",
    paragraphes: [
      "Le profil cognitif est une grille de lecture inspirée des typologies de personnalité modernes. À partir d'un questionnaire de douze questions, il évalue quatre dimensions fondamentales de votre fonctionnement mental : d'où vous tirez votre énergie, comment vous percevez le monde, comment vous prenez vos décisions et comment vous organisez votre vie. La combinaison de ces quatre axes définit l'un des seize profils possibles.",
      "C'est un outil d'auto-observation, pas une étiquette figée : les résultats peuvent évoluer selon les périodes de vie.",
    ],
  },

  dimensions: {
    titre: 'Que signifient vos résultats ?',
    items: [
      {
        nom: 'Énergie',
        description:
          "Introversion ou extraversion : préférez-vous puiser votre énergie dans la solitude et la réflexion, ou dans le contact avec les autres et l'action ?",
      },
      {
        nom: 'Perception',
        description:
          "Intuition ou sensation : êtes-vous davantage porté par les possibilités et les concepts, ou par les faits concrets et l'expérience directe ?",
      },
      {
        nom: 'Décision',
        description:
          "Ressenti ou raisonnement : vos choix s'appuient-ils plus sur vos valeurs et les émotions en jeu, ou sur une analyse logique et objective ?",
      },
      {
        nom: 'Organisation',
        description:
          "Structure ou souplesse : préférez-vous planifier et décider tôt, ou garder les options ouvertes le plus longtemps possible ?",
      },
    ],
  },

  resultatsPersonnalises: {
    "L'Architecte": { titre: "L'Architecte", texte: "Vous puisez votre énergie dans la réflexion solitaire, êtes tourné vers les concepts et les possibilités, décidez avec la logique et aimez planifier. Vous êtes probablement quelqu'un de visionnaire, indépendant et exigeant, avec une capacité rare à structurer des idées complexes sur le long terme." },
    'Le Logicien': { titre: 'Le Logicien', texte: "Vous puisez votre énergie dans l'introspection, êtes attiré par les concepts, analysez avec rigueur et gardez vos options ouvertes. Vous êtes probablement quelqu'un de curieux, réservé et méthodique, animé par une soif de comprendre en profondeur le fonctionnement des choses et des systèmes." },
    'Le Protecteur': { titre: 'Le Protecteur', texte: "Vous puisez votre énergie dans le recueillement, êtes porté par l'intuition, décidez selon vos valeurs et aimez organiser votre vie. Vous êtes probablement quelqu'un de sensible, profond et engagé, avec une vision claire de ce qui a du sens pour vous et un souci authentique du bien-être des autres." },
    'Le Médiateur': { titre: 'Le Médiateur', texte: "Vous puisez votre énergie dans le monde intérieur, êtes tourné vers les possibilités, écoutez vos valeurs et privilégiez la souplesse. Vous êtes probablement quelqu'un de créatif, empathique et attaché à l'authenticité, avec un univers intérieur riche et un besoin fort de cohérence entre vos actes et vos convictions." },
    'Le Logisticien': { titre: 'Le Logisticien', texte: "Vous puisez votre énergie dans le calme, êtes ancré dans le concret, décidez avec logique et aimez la structure. Vous êtes probablement quelqu'un de fiable, méthodique et rigoureux, à qui l'on peut confier des responsabilités car vous menez à terme ce que vous entreprenez avec sérieux." },
    'Le Défenseur': { titre: 'Le Défenseur', texte: "Vous puisez votre énergie en retrait, êtes attentif aux détails concrets, décidez selon vos valeurs et aimez la stabilité. Vous êtes probablement quelqu'un de dévoué, attentionné et discret, qui prend soin des autres et de son environnement avec une constance et une loyauté remarquables." },
    'Le Virtuose': { titre: 'Le Virtuose', texte: "Vous puisez votre énergie dans la solitude, êtes attaché aux faits, raisonnez avec pragmatisme et gardez de la souplesse. Vous êtes probablement quelqu'un d'observateur, indépendant et habile de vos mains ou de votre esprit, avec un talent naturel pour comprendre comment les choses fonctionnent concrètement." },
    "L'Aventurier": { titre: "L'Aventurier", texte: "Vous puisez votre énergie dans le calme, êtes sensible à ce qui vous entoure, décidez avec le cœur et privilégiez la spontanéité. Vous êtes probablement quelqu'un de doux, esthète et authentique, avec une sensibilité fine et un besoin d'harmonie dans votre quotidien et vos relations." },
    'Le Commandant': { titre: 'Le Commandant', texte: "Vous puisez votre énergie dans l'action, êtes tourné vers les possibilités, analysez avec logique et aimez planifier. Vous êtes probablement quelqu'un de déterminé, stratégique et énergique, avec un talent naturel pour mobiliser les autres autour d'objectifs ambitieux et structurer les projets." },
    'Le Débatteur': { titre: 'Le Débatteur', texte: "Vous puisez votre énergie dans les échanges, êtes attiré par les idées nouvelles, raisonnez avec vivacité et aimez la spontanéité. Vous êtes probablement quelqu'un d'inventif, curieux et provocateur, qui se nourrit du débat, de la confrontation d'idées et de la découverte de possibilités inexplorées." },
    'Le Protagoniste': { titre: 'Le Protagoniste', texte: "Vous puisez votre énergie dans les relations, êtes tourné vers l'humain, décidez selon vos valeurs et aimez organiser. Vous êtes probablement quelqu'un de chaleureux, mobilisateur et attentif, capable de fédérer les autres autour d'une vision et de faire grandir ceux qui vous entourent." },
    "L'Inspirateur": { titre: "L'Inspirateur", texte: "Vous puisez votre énergie dans le contact, êtes porté par les possibilités, écoutez vos valeurs et gardez toutes les options ouvertes. Vous êtes probablement quelqu'un d'enthousiaste, imaginatif et chaleureux, avec un don pour insuffler de l'énergie et voir le potentiel unique en chaque personne." },
    'Le Directeur': { titre: 'Le Directeur', texte: "Vous puisez votre énergie dans l'action, êtes ancré dans le concret, raisonnez avec logique et aimez structurer. Vous êtes probablement quelqu'un d'efficace, direct et responsable, qui excelle à mettre en place des systèmes clairs et à faire avancer les choses de manière tangible." },
    'Le Consul': { titre: 'Le Consul', texte: "Vous puisez votre énergie dans les relations, êtes attentif aux besoins concrets des autres, décidez selon vos valeurs et aimez la structure. Vous êtes probablement quelqu'un de généreux, sociable et prévenant, qui crée du lien et veille à ce que chacun se sente accueilli et pris en compte." },
    "L'Entrepreneur": { titre: "L'Entrepreneur", texte: "Vous puisez votre énergie dans l'action, êtes attentif à ce qui se passe autour de vous, décidez avec pragmatisme et adorez la spontanéité. Vous êtes probablement quelqu'un de vif, réactif et audacieux, à l'aise dans l'action immédiate et dans les situations qui demandent de s'adapter vite." },
    "L'Animateur": { titre: "L'Animateur", texte: "Vous puisez votre énergie dans le contact, êtes ancré dans l'expérience directe, décidez avec le cœur et vivez dans l'instant. Vous êtes probablement quelqu'un de spontané, chaleureux et joyeux, qui apporte du dynamisme autour de vous et sait profiter pleinement du moment présent." },
  },

  // NOUVEAU : détails par pôle dominant sur chaque axe (8 textes).
  // Clé = axe (energie, perception, decision, organisation)
  // Sous-clé = valeur du champ "dominant" retourné par le backend
  detailsParValeur: {
    energie: {
      Introversion: {
        titre: 'Énergie · Introversion',
        texte:
          "Vous puisez votre énergie dans le calme, la réflexion solitaire et le monde intérieur. Après une période d'interactions intenses, un temps de retrait vous permet de recharger vos batteries. Ce n'est pas de la timidité, c'est un fonctionnement énergétique.",
      },
      Extraversion: {
        titre: 'Énergie · Extraversion',
        texte:
          "Vous puisez votre énergie dans le contact, l'action et le monde extérieur. Les échanges avec les autres, les stimulations variées et les nouveautés vous rechargent. La solitude prolongée peut vous peser plus qu'elle ne vous ressource.",
      },
    },
    perception: {
      Intuition: {
        titre: 'Perception · Intuition',
        texte:
          "Vous percevez le monde d'abord par les concepts, les possibilités et les liens cachés. Votre attention se porte naturellement sur ce qui pourrait advenir, sur les schémas d'ensemble et sur la signification profonde des choses.",
      },
      Sensation: {
        titre: 'Perception · Sensation',
        texte:
          "Vous percevez le monde d'abord par les faits concrets, l'expérience directe et les détails observables. Votre attention se porte naturellement sur ce qui existe déjà, sur les preuves tangibles et sur l'utilité pratique.",
      },
    },
    decision: {
      Sentiment: {
        titre: 'Décision · Sentiment',
        texte:
          "Vous prenez vos décisions d'abord en écoutant vos valeurs personnelles, les émotions en jeu et l'impact humain. Vous cherchez ce qui est juste pour les personnes concernées, y compris vous-même, avant ce qui est purement rationnel.",
      },
      Raisonnement: {
        titre: 'Décision · Raisonnement',
        texte:
          "Vous prenez vos décisions d'abord par une analyse logique et objective. Vous cherchez la cohérence, la cause réelle et l'efficacité, en mettant temporairement de côté les émotions pour arriver à un jugement clair.",
      },
    },
    organisation: {
      Jugement: {
        titre: 'Organisation · Jugement',
        texte:
          "Vous préférez planifier, décider tôt et cadrer votre environnement. Un fil conducteur clair vous rassure et vous permet d'avancer sereinement. Vous êtes à l'aise avec les décisions fermes et les engagements pris.",
      },
      Perception: {
        titre: 'Organisation · Perception',
        texte:
          "Vous préférez garder les options ouvertes, décider au dernier moment et laisser la vie apporter ses opportunités. La flexibilité est votre force, et vous savez rebondir face aux imprévus mieux que la plupart.",
      },
    },
  },
};

export function getResultatProfilCognitif(nomProfil) {
  return profilCognitifContenu.resultatsPersonnalises[nomProfil] || null;
}

// NOUVEAU : renvoie le détail pour un pôle dominant d'un axe cognitif.
// axe : 'energie' | 'perception' | 'decision' | 'organisation'
// dominant : "Introversion" | "Extraversion" | "Intuition" | ...
// Ex: getDetailProfilCognitif('energie', 'Introversion') → { titre, texte }
export function getDetailProfilCognitif(axe, dominant) {
  const axeData = profilCognitifContenu.detailsParValeur[axe];
  if (!axeData) return null;
  return axeData[dominant] || null;
}
