import { useState, useEffect, useRef } from 'react';

/**
 * Modale d'affichage d'un lien de partage public.
 *
 * Props :
 * - isOpen : booleen, controle l'affichage
 * - url : string, URL complete a partager (ex: "http://localhost:5173/public/abc123...")
 * - expiresAt : string ISO 8601, date d'expiration du lien
 * - onClose : callback de fermeture
 */
function ShareDialog({ isOpen, url, expiresAt, onClose }) {
  const [copied, setCopied] = useState(false);
  const inputRef = useRef(null);

  // Fermeture par Echap (coherent avec ConfirmDialog)
  useEffect(() => {
    if (!isOpen) return;
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Reset du feedback "Copie" quand la modale se ferme/rouvre
  useEffect(() => {
    if (!isOpen) setCopied(false);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      // Reset du feedback apres 2 secondes
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      // Fallback pour les anciens navigateurs : selectionner le texte
      // L'utilisateur fera Ctrl+C manuellement
      console.error('Echec copie automatique :', err);
      inputRef.current?.select();
    }
  };

  // Format date d'expiration en francais
  const dateExpiration = new Date(expiresAt).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="share-dialog-title"
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id="share-dialog-title"
          className="text-lg font-semibold text-gray-900 mb-2"
        >
          Lien de partage cree
        </h2>

        <p className="text-sm text-gray-600 mb-4">
          Toute personne avec ce lien pourra consulter le profil
          (sauf la synthese personnelle) jusqu'au {dateExpiration}.
        </p>

        {/* Champ + bouton copier */}
        <div className="flex gap-2 mb-6">
          <input
            ref={inputRef}
            type="text"
            value={url}
            readOnly
            onClick={(e) => e.target.select()}
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded bg-gray-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={handleCopy}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              copied
                ? 'bg-green-600 text-white'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }`}
          >
            {copied ? 'Copie ✓' : 'Copier'}
          </button>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}

export default ShareDialog;
