import AboutSection from './AboutSection';
import ValeurDetail from './ValeurDetail';
import {
  numerologieContenu,
  getResultatNumerologie,
  getDetailNumerologie,
} from '../../content/theories/numerologie';

// Carte affichant les 4 nombres de la numerologie en grille 2x2 cliquable.
//
// Props :
//   numerologie : { chemin_vie, expression, intime, realisation }
export default function CarteNumerologie({ numerologie }) {
  const valeurs = [
    {
      cle: 'chemin_vie',
      label: 'Chemin de vie',
      valeur: numerologie.chemin_vie,
      detail: getDetailNumerologie('chemin_vie', numerologie.chemin_vie),
    },
    {
      cle: 'expression',
      label: 'Expression',
      valeur: numerologie.expression,
      detail: getDetailNumerologie('expression', numerologie.expression),
    },
    {
      cle: 'intime',
      label: 'Intime',
      valeur: numerologie.intime,
      detail: getDetailNumerologie('intime', numerologie.intime),
    },
    {
      cle: 'realisation',
      label: 'Réalisation',
      valeur: numerologie.realisation,
      detail: getDetailNumerologie('realisation', numerologie.realisation),
    },
  ];

  const resultatPersonnalise = getResultatNumerologie(numerologie.chemin_vie);

  return (
    <div className="border rounded-lg p-5 bg-white">
      <h3 className="text-xl font-serif mb-4 text-ensoi-primary">Numérologie</h3>

      <ValeurDetail valeurs={valeurs} layout="grid" />

      <AboutSection
        contenu={numerologieContenu}
        resultatPersonnalise={resultatPersonnalise}
      />
    </div>
  );
}
