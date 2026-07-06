// Bloc affichant la synthese IA generee par Groq. Affiche la synthese
// formatee (avec paragraphes separes visuellement) si disponible,
// sinon un message explicatif.
//
// Le decoupage explicite par paragraphes garantit un rendu coherent
// entre l'UI et le PDF (pdfExport.js applique la meme logique).
//
// Props :
//   synthese : string | null
//   statut   : 'complet' | 'partiel'
export default function BlocSynthese({ synthese, statut }) {
  if (statut === 'partiel' || !synthese) {
    return (
      <div className="border rounded-lg p-5 bg-amber-50 border-amber-200">
        <h3 className="text-xl font-serif mb-2 text-amber-800">
          Synthèse IA non disponible
        </h3>
        <p className="text-sm text-amber-700">
          La synthese personnalisee n'a pas pu etre generee. Les calculs
          ci-dessus restent complets et valides. Vous pouvez regenerer un
          profil plus tard pour obtenir la synthese.
        </p>
      </div>
    );
  }

  // Decoupage par paragraphes (le modele Groq retourne \n\n entre chaque §).
  // Meme logique que dans frontend/src/services/pdfExport.js pour un rendu
  // coherent entre l'affichage web et l'export PDF.
  const paragraphes = synthese
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter((p) => p.length > 0);

  return (
    <div className="border rounded-lg p-5 bg-white">
      <h3 className="text-xl font-serif mb-3 text-ensoi-primary">
        Synthèse personnalisée
      </h3>
      <div className="max-w-none text-gray-700">
        {paragraphes.map((paragraphe, index) => (
          <p key={index} className="mb-4 last:mb-0 leading-relaxed">
            {paragraphe}
          </p>
        ))}
      </div>
    </div>
  );
}
