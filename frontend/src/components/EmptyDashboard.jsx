import { useNavigate } from 'react-router-dom';

/**
 * Composant affiche quand l'utilisateur n'a aucun profil dans son dashboard.
 *
 * Pattern UX : etat vide + CTA principal. L'utilisateur fraichement inscrit
 * voit immediatement quelle est l'action attendue (generer son premier profil).
 */
function EmptyDashboard() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <h2 className="text-2xl font-semibold text-gray-900 mb-3">
        Aucun profil pour le moment
      </h2>

      <p className="text-gray-600 max-w-md mb-8">
        Generez votre premier profil pour decouvrir votre numerologie, votre
        Human Design et votre type cognitif.
      </p>

      <button
        onClick={() => navigate('/generer')}
        className="px-6 py-3 bg-ensoi-primary text-white font-medium rounded-lg hover:bg-ensoi-dark transition-colors shadow-md hover:shadow-lg"
      >
        Generer mon premier profil
      </button>
    </div>
  );
}

export default EmptyDashboard;
