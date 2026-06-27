import { useState } from 'react';
import { useProfils } from '../hooks/useProfils';
import ProfilCard from '../components/ProfilCard';
import EmptyDashboard from '../components/EmptyDashboard';
import ConfirmDialog from '../components/ConfirmDialog';
import ShareDialog from '../components/ShareDialog';
import { profilsApi } from '../api/client';

/**
 * Page Dashboard : liste des profils de l'utilisateur connecte.
 *
 * Etats geres :
 * - loading : chargement initial (squelette/spinner)
 * - error : echec reseau (message + bouton reessayer)
 * - empty : utilisateur sans profil (CTA vers /generer)
 * - liste : affichage des cartes ProfilCard
 *
 * Actions :
 * - Suppression : ouvre ConfirmDialog, puis appelle removeProfil du hook
 *   (suppression optimiste, restauration en cas d'echec)
 * - Partage / Export PDF : placeholders, implementation sur les branches dediees
 */
function DashboardPage() {
  const { profils, loading, error, refetch, removeProfil } = useProfils();

  // Etat de la modale de confirmation de suppression
  const [profilToDelete, setProfilToDelete] = useState(null);
  const [deleteError, setDeleteError] = useState(null);
  // Etat de la modale de partage
  const [shareData, setShareData] = useState(null);
  const [shareError, setShareError] = useState(null);

  const handleAskDelete = (id) => {
    setDeleteError(null);
    setProfilToDelete(id);
  };

  const handleConfirmDelete = async () => {
    const id = profilToDelete;
    setProfilToDelete(null);
    try {
      await removeProfil(id);
    } catch (err) {
      setDeleteError(
        err.response?.data?.detail ||
        'La suppression a echoue. Le profil a ete restaure.'
      );
    }
  };

  const handleShare = async (id) => {
    setShareError(null);
    try {
      const response = await profilsApi.share(id);
      setShareData(response.data);
    } catch (err) {
      console.error('handleShare:', err);
      setShareError(
        err.response?.data?.detail ||
        'Impossible de creer le lien de partage. Reessayez plus tard.'
      );
    }
  };

  const handleExport = (id) => {
    // TODO : implementation sur feature/export-pdf
    alert(`Export PDF du profil ${id} : bientot disponible.`);
  };

  // Etat de chargement initial
  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Mes profils
        </h1>
        <div className="flex items-center justify-center py-16">
          <div className="text-gray-500">Chargement de vos profils…</div>
        </div>
      </div>
    );
  }

  // Etat d'erreur reseau
  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Mes profils
        </h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 mb-4">{error}</p>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Reessayer
          </button>
        </div>
      </div>
    );
  }

  // Etat vide
  if (profils.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Mes profils
        </h1>
        <EmptyDashboard />
      </div>
    );
  }

  // Etat normal : liste des profils
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <header className="flex justify-between items-baseline mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Mes profils
        </h1>
        <span className="text-sm text-gray-500">
          {profils.length} profil{profils.length > 1 ? 's' : ''}
        </span>
      </header>

      {/* Banniere d'erreur de suppression (suppression a echoue, profil restaure) */}
      {deleteError && (
        <div className="mb-4 bg-amber-50 border border-amber-200 rounded p-3 text-sm text-amber-800">
          {deleteError}
        </div>
      )}

      {/* Banniere d'erreur de partage */}
      {shareError && (
        <div className="mb-4 bg-amber-50 border border-amber-200 rounded p-3 text-sm text-amber-800">
          {shareError}
        </div>
      )}

      {/* Grille des cartes profils */}
      <div className="grid gap-4 md:grid-cols-2">
        {profils.map((profil) => (
          <ProfilCard
            key={profil.id}
            profil={profil}
            onDelete={handleAskDelete}
            onShare={handleShare}
            onExport={handleExport}
          />
        ))}
      </div>

      {/* Modale de confirmation suppression */}
      <ConfirmDialog
        isOpen={profilToDelete !== null}
        title="Supprimer ce profil ?"
        message="Cette action est irreversible. Toutes les donnees du profil seront supprimees definitivement."
        confirmLabel="Supprimer"
        cancelLabel="Annuler"
        destructive={true}
        onConfirm={handleConfirmDelete}
        onCancel={() => setProfilToDelete(null)}
      />
      
      {/* Modale de partage */}
      <ShareDialog
        isOpen={shareData !== null}
        url={shareData?.url}
        expiresAt={shareData?.expires_at}
        onClose={() => setShareData(null)}
      />
    </div>
  );
}

export default DashboardPage;
