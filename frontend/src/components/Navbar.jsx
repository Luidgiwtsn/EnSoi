import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Barre de navigation globale.
 *
 * - Logo EnSoi a gauche (lien vers /).
 * - A droite, change selon l'etat d'authentification :
 *   - Connecte : prenom de l'utilisateur, liens Mon historique et Generer,
 *     bouton Deconnexion.
 *   - Anonyme : boutons Se connecter et S'inscrire, plus un lien Generer
 *     (la page reste accessible aux anonymes pour le scenario 3).
 *
 * Pendant le bootstrap de l'AuthContext (loading=true), on n'affiche aucun
 * bouton d'action pour eviter un flash "Se connecter -> Bonjour Marie" au F5.
 */
export default function Navbar() {
  const { user, isAuthenticated, loading, logout } = useAuth();
  const navigate = useNavigate();
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    await logout();
    setLoggingOut(false);
    navigate('/', { replace: true });
  };

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="container mx-auto px-6 py-3 flex items-center justify-between">
        <Link to="/" className="text-2xl font-serif text-ensoi-primary">
          EnSoi
        </Link>

        <div className="flex items-center gap-3">
          {loading ? (
            // Placeholder discret pendant le bootstrap pour eviter le flash
            <span className="text-ensoi-muted text-sm">...</span>
          ) : isAuthenticated ? (
            <>
              <Link
                to="/generer"
                className="text-sm text-ensoi-muted hover:text-ensoi-primary"
              >
                Générer
              </Link>
              <Link
                to="/dashboard"
                className="text-sm text-ensoi-muted hover:text-ensoi-primary"
              >
                Mon historique
              </Link>
              <span className="text-sm font-medium ml-2">
                {user?.prenom} {user?.nom_famille}
              </span>
              <button
                onClick={handleLogout}
                disabled={loggingOut}
                className="text-sm px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
              >
                {loggingOut ? '...' : 'Déconnexion'}
              </button>
            </>
          ) : (
            <>
              <Link
                to="/generer"
                className="text-sm text-ensoi-muted hover:text-ensoi-primary"
              >
                Générer
              </Link>
              <Link to="/login" className="btn-secondary text-sm">
                Se connecter
              </Link>
              <Link to="/register" className="btn-primary text-sm">
                S'inscrire
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
