import { useState, useEffect, useCallback } from 'react';
import { profilsApi } from '../api/client';

/**
 * Hook de gestion de la liste des profils de l'utilisateur connecte.
 *
 * Retourne :
 * - profils : liste des profils (triee par created_at desc cote backend)
 * - loading : true pendant le fetch initial uniquement
 * - error : message d'erreur si echec, null sinon
 * - refetch : recharge la liste depuis le serveur
 * - removeProfil(id) : supprime un profil cote serveur puis l'enleve de la liste
 *                      (suppression optimiste : retire localement immediatement,
 *                       restaure en cas d'echec serveur)
 */
export function useProfils() {
  const [profils, setProfils] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProfils = useCallback(async () => {
    setError(null);
    try {
      const response = await profilsApi.list();
      setProfils(response.data);
    } catch (err) {
      console.error('useProfils.fetchProfils:', err);
      setError(
        err.response?.data?.detail ||
        'Impossible de charger vos profils. Verifiez votre connexion.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Chargement initial au montage du composant
  useEffect(() => {
    fetchProfils();
  }, [fetchProfils]);

  /**
   * Supprime un profil avec strategie optimiste :
   * 1. Retire le profil de la liste affichee immediatement (feedback instantane)
   * 2. Envoie la requete DELETE au serveur
   * 3. Si echec, restaure le profil dans la liste et propage l'erreur
   */
  const removeProfil = useCallback(async (id) => {
    const profilSupprime = profils.find((p) => p.id === id);
    if (!profilSupprime) return;

    // Suppression optimiste cote UI
    setProfils((prev) => prev.filter((p) => p.id !== id));

    try {
      await profilsApi.delete(id);
    } catch (err) {
      // Restauration en cas d'echec : on remet le profil a sa place initiale
      setProfils((prev) => {
        const restored = [...prev, profilSupprime];
        return restored.sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );
      });
      throw err;
    }
  }, [profils]);

  return {
    profils,
    loading,
    error,
    refetch: fetchProfils,
    removeProfil,
  };
}
