import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Garde-fou cote frontend pour les routes protegees.
 *
 * - Tant que loading=true (bootstrap initial de l'AuthContext en cours),
 *   affiche un placeholder pour eviter un flash vers /login pendant la verif.
 * - Si l'utilisateur n'est pas authentifie, redirige vers /login en passant
 *   l'URL d'origine en state.from pour redirection apres connexion.
 * - Sinon, rend les enfants normalement.
 *
 * Important : ceci est uniquement de l'UX. La securite est assuree par le
 * backend qui rejette les requetes sans Bearer token valide. PrivateRoute
 * sert juste a eviter d'afficher une page vide ou cassee a un visiteur non
 * connecte.
 */
export default function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="container mx-auto p-6 text-ensoi-muted">
        Chargement...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}
