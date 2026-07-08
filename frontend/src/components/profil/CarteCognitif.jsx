import { useState } from 'react';
import AboutSection from './AboutSection';
import {
  profilCognitifContenu,
  getResultatProfilCognitif,
  getDetailProfilCognitif,
} from '../../content/theories/profilCognitif';

// Carte affichant le profil cognitif : type, nom et 4 dimensions avec
// barres de progression cliquables pour voir le détail du pôle dominant.
//
// Props :
//   cognitif : { nom_profil, dimensions: { energie, perception, decision, organisation } }
export default function CarteCognitif({ cognitif }) {
  const axes = [
    { cle: 'energie', label: 'Énergie' },
    { cle: 'perception', label: 'Perception' },
    { cle: 'decision', label: 'Décision' },
    { cle: 'organisation', label: 'Organisation' },
  ];

  const [axeActif, setAxeActif] = useState(null);

  const resultatPersonnalise = getResultatProfilCognitif(cognitif.nom_profil);

  const handleClic = (cle) => {
    setAxeActif((prev) => (prev === cle ? null : cle));
  };

  const detailActif = axeActif
    ? getDetailProfilCognitif(axeActif, cognitif.dimensions[axeActif]?.dominant)
    : null;

  return (
    <div className="border rounded-lg p-5 bg-white">
      <h3 className="text-xl font-serif mb-1 text-ensoi-primary">
        Profil cognitif
      </h3>
      <div className="text-sm text-gray-500 mb-4">
        {cognitif.nom_profil}
      </div>
      <div className="space-y-3">
        {axes.map(({ cle, label }) => {
          const dim = cognitif.dimensions[cle];
          const isActive = axeActif === cle;
          return (
            <button
              key={cle}
              type="button"
              onClick={() => handleClic(cle)}
              className={`w-full text-left p-2 rounded-md transition-all ${
                isActive
                  ? 'bg-ensoi-secondary/10 ring-1 ring-ensoi-primary/40'
                  : 'hover:bg-gray-50 cursor-pointer'
              }`}
            >
              <div className="flex justify-between text-xs mb-1">
                <span className="uppercase text-gray-500">{label}</span>
                <span className="font-medium">
                  {dim.dominant} - {dim.score_pourcentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-ensoi-primary h-2 rounded-full transition-all"
                  style={{ width: `${dim.score_pourcentage}%` }}
                />
              </div>
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

      <AboutSection
        contenu={profilCognitifContenu}
        resultatPersonnalise={resultatPersonnalise}
      />
    </div>
  );
}
