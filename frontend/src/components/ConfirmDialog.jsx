import { useEffect } from 'react';

/**
 * Modale generique de confirmation pour actions destructives.
 *
 * Props :
 * - isOpen : booleen, controle l'affichage
 * - title : titre de la modale (ex: "Supprimer ce profil ?")
 * - message : texte explicatif (ex: "Cette action est irreversible.")
 * - confirmLabel : texte du bouton de confirmation (defaut: "Confirmer")
 * - cancelLabel : texte du bouton d'annulation (defaut: "Annuler")
 * - onConfirm : callback appele quand l'utilisateur confirme
 * - onCancel : callback appele quand l'utilisateur annule ou ferme
 * - destructive : si true, le bouton de confirmation est rouge (defaut: false)
 */
function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirmer',
  cancelLabel = 'Annuler',
  onConfirm,
  onCancel,
  destructive = false,
}) {
  // Fermeture via la touche Echap
  useEffect(() => {
    if (!isOpen) return;
    const handleEscape = (e) => {
      if (e.key === 'Escape') onCancel();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  const confirmButtonClass = destructive
    ? 'bg-red-600 hover:bg-red-700 text-white'
    : 'bg-ensoi-primary hover:bg-ensoi-dark text-white';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
    >
      {/* stopPropagation pour ne pas fermer la modale en cliquant dedans */}
      <div
        className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id="confirm-dialog-title"
          className="text-lg font-semibold text-gray-900 mb-2"
        >
          {title}
        </h2>

        <p className="text-sm text-gray-600 mb-6">
          {message}
        </p>

        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${confirmButtonClass}`}
            autoFocus
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
