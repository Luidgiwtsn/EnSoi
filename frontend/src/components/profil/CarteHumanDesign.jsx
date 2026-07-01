// Carte affichant le profil Human Design.
//
// Props :
//   humanDesign : { type_hd, strategie, profil, autorite, donnees_completes }

export default function CarteHumanDesign({ humanDesign }) {
  const lignes = [
    { label: 'Type', valeur: humanDesign.type_hd },
    { label: 'Stratégie', valeur: humanDesign.strategie },
    { label: 'Profil', valeur: humanDesign.profil },
    { label: 'Autorité', valeur: humanDesign.autorite },
  ];

  return (
    <div className="border rounded-lg p-5 bg-white">
      <h3 className="text-xl font-serif mb-4 text-ensoi-primary">Human Design</h3>

      <div className="space-y-3">
        {lignes.map(({ label, valeur }) => (
          <div key={label}>
            <div className="text-xs uppercase text-gray-500">{label}</div>
            <div className="font-medium">{valeur}</div>
          </div>
        ))}
      </div>

      {!humanDesign.donnees_completes && (
        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
          Calcul approximatif : pour plus de precision, indiquez votre heure
          et lieu de naissance lors de la generation du profil.
        </div>
      )}
    </div>
  );
}
