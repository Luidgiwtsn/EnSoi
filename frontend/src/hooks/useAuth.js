import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

/**
 * Hook pour acceder a l'etat d'authentification depuis n'importe quel composant.
 * Doit etre utilise a l'interieur d'un <AuthProvider>.
 *
 * Usage : const { user, isAuthenticated, login, logout, loading } = useAuth();
 */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (ctx === null) {
    throw new Error("useAuth doit etre utilise a l'interieur d'un AuthProvider");
  }
  return ctx;
}
