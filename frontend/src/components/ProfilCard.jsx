import { useNavigate } from 'react-router-dom';

/**
 * Carte d'affichage d'un profil dans le dashboard.
 *
 * Props :
 * - profil : objet ProfilComplet retourne par le backend
 * - onDelete : (id) => void, callback quand l'utilisateur confirme la suppression
 * - onShare : (id) => void, placeholder (implementation sur feature/share-public)
 * - onExport : (id) => void, placeholder (implementation sur feature/export-pdf)
 */
function ProfilCard({ profil, onDelete, onShare, onExport }) {
  const navigate = useNavigate();

  // Extrait des donnees pour affichage
  const cheminVie = profil.numerologie?.chemin_vie ?? '—';
  const typeHD = profil.human_design?.type_hd ?? '—';
  const typeCognitif = profil.profil_cognitif?.nom_profil ?? '—';

  // Synthese : on tronque a ~150 caracteres pour l'apercu
  const synthese = profil.synthese_ia;
  const apercu = synthese
    ? synthese.length > 150
      ? `${synthese.slice(0, 150).trim()}…`
      : synthese
    : null;

  // Formatage de la date de creation (JJ/MM/AAAA)
  const dateCreation = new Date(profil.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });

  const handleVoir = () => navigate(`/profils/${profil.id}`);

  return (
    <article className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* En-tete : nom + date de creation */}
      <header className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            {profil.prenom} {profil.nom_famille}
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Genere le {dateCreation}
          </p>
        </div>
        {profil.statut === 'partiel' && (
          <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">
            Partiel
          </span>
        )}
      </header>

      {/* Donnees cles : 3 chiffres/types en grille */}
      <dl className="grid grid-cols-3 gap-3 mb-4 text-sm">
        <div>
          <dt className="text-gray-500">Chemin de vie</dt>
          <dd className="font-medium text-gray-900">{cheminVie}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Human Design</dt>
          <dd className="font-medium text-gray-900">{typeHD}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Cognitif</dt>
          <dd className="font-medium text-gray-900">{typeCognitif}</dd>
        </div>
      </dl>

      {/* Apercu synthese IA */}
      <div className="mb-4">
        {apercu ? (
          <p className="text-sm text-gray-700 italic leading-relaxed">
            « {apercu} »
          </p>
        ) : (
          <p className="text-sm text-gray-400 italic">
            Synthese non disponible (Groq etait indisponible lors de la generation).
          </p>
        )}
      </div>

      {/* Actions */}
      <footer className="flex flex-wrap gap-2 pt-3 border-t border-gray-100">
        <button
          onClick={handleVoir}
          className="px-3 py-1.5 text-sm bg-ensoi-primary text-white rounded hover:bg-ensoi-dark transition-colors"
        >
          Voir
        </button>
        <button
          onClick={() => onShare(profil.id)}
          className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
        >
          Partager
        </button>
        <button
          onClick={() => onExport(profil.id)}
          className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
        >
          Exporter PDF
        </button>
        <button
          onClick={() => onDelete(profil.id)}
          className="px-3 py-1.5 text-sm bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors ml-auto"
        >
          Supprimer
        </button>
      </footer>
    </article>
  );
}

export default ProfilCard;
