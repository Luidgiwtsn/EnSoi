import { useState } from 'react';

// Composant réutilisable : section "En savoir plus" repliable en bas d'une carte.
//
// Props :
//   contenu              : objet { titre, intro, dimensions } issu de content/theories/*.js
//   resultatPersonnalise : objet { titre, texte } ou null si non disponible
export default function AboutSection({ contenu, resultatPersonnalise }) {
  const [ouvert, setOuvert] = useState(false);

  return (
    <div className="mt-5 pt-4 border-t border-gray-200">
      <button
        type="button"
        onClick={() => setOuvert(!ouvert)}
        className="w-full flex items-center justify-between text-sm text-gray-500 hover:text-ensoi-primary transition-colors"
        aria-expanded={ouvert}
      >
        <span className="italic">
          {ouvert ? 'Réduire' : `En savoir plus sur ${contenu.titre}`}
        </span>
        <span className="text-xs" aria-hidden="true">
          {ouvert ? '▲' : '▼'}
        </span>
      </button>

      {ouvert && (
        <div className="mt-4 space-y-5 text-sm text-gray-700 leading-relaxed">
          <section>
            <h4 className="font-serif text-base text-ensoi-primary mb-2">
              {contenu.intro.titre}
            </h4>
            {contenu.intro.paragraphes.map((paragraphe, index) => (
              <p key={index} className={index > 0 ? 'mt-2' : ''}>
                {paragraphe}
              </p>
            ))}
          </section>

          <section>
            <h4 className="font-serif text-base text-ensoi-primary mb-2">
              {contenu.dimensions.titre}
            </h4>
            <ul className="space-y-2">
              {contenu.dimensions.items.map((item) => (
                <li key={item.nom}>
                  <span className="font-medium text-ensoi-primary">
                    {item.nom}
                  </span>{' '}
                  - {item.description}
                </li>
              ))}
            </ul>
          </section>

          {resultatPersonnalise && (
            <section>
              <h4 className="font-serif text-base text-ensoi-primary mb-2">
                Votre résultat en un coup d'œil
              </h4>
              <p>
                <span className="font-medium">
                  {resultatPersonnalise.titre}
                </span>{' '}
                - {resultatPersonnalise.texte}
              </p>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
