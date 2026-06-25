// Carte affichant les 4 nombres de la numerologie en grille 2x2.
//
// Props :
//   numerologie : { chemin_vie, expression, intime, realisation }

export default function CarteNumerologie({ numerologie }) {
  const items = [
    { label: 'Chemin de vie', valeur: numerologie.chemin_vie },
    { label: 'Expression', valeur: numerologie.expression },
    { label: 'Intime', valeur: numerologie.intime },
    { label: 'Realisation', valeur: numerologie.realisation },
  ];

  return (
    <div className="border rounded-lg p-5 bg-white">
      <h3 className="text-xl font-serif mb-4 text-ensoi-primary">Numerologie</h3>
      <div className="grid grid-cols-2 gap-4">
        {items.map((item) => (
          <div key={item.label} className="text-center">
            <div className="text-4xl font-serif text-ensoi-primary">
              {item.valeur}
            </div>
            <div className="text-xs uppercase text-gray-500 mt-1">
              {item.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
