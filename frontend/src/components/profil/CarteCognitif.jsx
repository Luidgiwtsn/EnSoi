// Carte affichant le profil cognitif : type, nom et 4 dimensions avec
// barre de progression par dimension.
//
// Props :
//   cognitif : { type_cognitif, nom_profil, dimensions: { energie, perception, decision, organisation } }

export default function CarteCognitif({ cognitif }) {
  const axes = [
    { cle: 'energie', label: 'Énergie' },
    { cle: 'perception', label: 'Perception' },
    { cle: 'decision', label: 'Décision' },
    { cle: 'organisation', label: 'Organisation' },
  ];

  return (
    <div className="border rounded-lg p-5 bg-white">
      <h3 className="text-xl font-serif mb-1 text-ensoi-primary">
        Profil cognitif
      </h3>
      <div className="text-sm text-gray-500 mb-4">
        {cognitif.type_cognitif} : {cognitif.nom_profil}
      </div>

      <div className="space-y-3">
        {axes.map(({ cle, label }) => {
          const dim = cognitif.dimensions[cle];
          return (
            <div key={cle}>
              <div className="flex justify-between text-xs mb-1">
                <span className="uppercase text-gray-500">{label}</span>
                <span className="font-medium">
                  {dim.dominant} ({dim.lettre}) - {dim.score_pourcentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-ensoi-primary h-2 rounded-full transition-all"
                  style={{ width: `${dim.score_pourcentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
