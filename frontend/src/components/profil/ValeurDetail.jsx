import { useState } from 'react';

// Composant Variante C : rend chaque valeur cliquable et affiche un bloc info
// sous la grille au clic. Un seul détail actif à la fois.
//
// Props :
//   valeurs : Array<{ cle, label, valeur, detail }> où
//     - cle    : identifiant unique de la valeur (ex: 'chemin_vie', 'type_hd')
//     - label  : intitulé affiché sous la valeur (ex: 'Chemin de vie')
//     - valeur : valeur affichée (ex: 7, "Générateur")
//     - detail : { titre, texte } ou null si aucun détail disponible
//   layout   : 'grid' (numérologie) ou 'stack' (HD) : influence le rendu de la grille
//   renderValeur : fonction optionnelle (valeurs, isActive, onClick) pour custom render
export default function ValeurDetail({ valeurs, layout = 'grid' }) {
  const [cleActive, setCleActive] = useState(null);

  const handleClic = (cle) => {
    setCleActive((prev) => (prev === cle ? null : cle));
  };

  const detailActif = valeurs.find((v) => v.cle === cleActive)?.detail;

  const containerClass =
    layout === 'grid' ? 'grid grid-cols-2 gap-4' : 'space-y-3';

  return (
    <div>
      <div className={containerClass}>
        {valeurs.map((v) => {
          const isActive = cleActive === v.cle;
          const isClickable = !!v.detail;

          if (layout === 'grid') {
            return (
              <button
                key={v.cle}
                type="button"
                onClick={() => isClickable && handleClic(v.cle)}
                disabled={!isClickable}
                className={`text-center p-2 rounded-md transition-all ${
                  isActive
                    ? 'bg-ensoi-secondary/10 ring-1 ring-ensoi-primary/40'
                    : isClickable
                    ? 'hover:bg-gray-50 cursor-pointer'
                    : 'cursor-default'
                }`}
              >
                <div className="text-4xl font-serif text-ensoi-primary">
                  {v.valeur}
                </div>
                <div className="text-xs uppercase text-gray-500 mt-1">
                  {v.label}
                </div>
              </button>
            );
          }

          // layout 'stack' pour HD
          return (
            <button
              key={v.cle}
              type="button"
              onClick={() => isClickable && handleClic(v.cle)}
              disabled={!isClickable}
              className={`w-full text-left p-2 rounded-md transition-all ${
                isActive
                  ? 'bg-ensoi-secondary/10 ring-1 ring-ensoi-primary/40'
                  : isClickable
                  ? 'hover:bg-gray-50 cursor-pointer'
                  : 'cursor-default'
              }`}
            >
              <div className="text-xs uppercase text-gray-500">{v.label}</div>
              <div className="font-medium">{v.valeur}</div>
            </button>
          );
        })}
      </div>

      {detailActif && (
        <div className="mt-4 p-4 bg-ensoi-secondary/10 border-l-2 border-ensoi-primary rounded">
          <div className="font-serif text-sm text-ensoi-primary mb-2">
            {detailActif.titre}
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {detailActif.texte}
          </p>
        </div>
      )}
    </div>
  );
}
