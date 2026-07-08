import AboutSection from './AboutSection';
import ValeurDetail from './ValeurDetail';
import {
  humanDesignContenu,
  getResultatHumanDesign,
  getDetailHumanDesign,
} from '../../content/theories/humanDesign';

// Carte affichant le profil Human Design avec valeurs cliquables.
//
// Props :
//   humanDesign : { type_hd, strategie, profil, autorite, donnees_completes }
export default function CarteHumanDesign({ humanDesign }) {
  const valeurs = [
    {
      cle: 'type_hd',
      label: 'Type',
      valeur: humanDesign.type_hd,
      detail: getDetailHumanDesign('type_hd', humanDesign.type_hd),
    },
    {
      cle: 'strategie',
      label: 'Stratégie',
      valeur: humanDesign.strategie,
      detail: getDetailHumanDesign('strategie', humanDesign.strategie),
    },
    {
      cle: 'profil',
      label: 'Profil',
      valeur: humanDesign.profil,
      detail: getDetailHumanDesign('profil', humanDesign.profil),
    },
    {
      cle: 'autorite',
      label: 'Autorité',
      valeur: humanDesign.autorite,
      detail: getDetailHumanDesign('autorite', humanDesign.autorite),
    },
  ];

  const resultatPersonnalise = getResultatHumanDesign(humanDesign.type_hd);

  return (
    <div className="border rounded-lg p-5 bg-white">
      <h3 className="text-xl font-serif mb-4 text-ensoi-primary">Human Design</h3>

      <ValeurDetail valeurs={valeurs} layout="stack" />

      {!humanDesign.donnees_completes && (
        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
          Calcul approximatif : pour plus de precision, indiquez votre heure
          et lieu de naissance lors de la generation du profil.
        </div>
      )}

      <AboutSection
        contenu={humanDesignContenu}
        resultatPersonnalise={resultatPersonnalise}
      />
    </div>
  );
}
