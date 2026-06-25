import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import { useAuth } from '../hooks/useAuth';

/**
 * Page /login - orchestre le formulaire et le flow d'authentification.
 *
 * Logique :
 * 1. Si deja connecte, redirige vers /dashboard immediatement (eviter de
 *    laisser un utilisateur connecte voir le formulaire de login).
 * 2. Sur submit, appelle login() du AuthContext.
 * 3. Si l'AuthContext a effectue un claim post-login (claimedProfilId != null),
 *    redirige vers /profils/{id} pour montrer le profil rattache.
 * 4. Sinon, redirige vers la route d'origine (state.from si on venait d'une
 *    PrivateRoute) ou vers /dashboard par defaut.
 * 5. En cas d'erreur, mappe le code HTTP en message utilisateur clair.
 */
export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState(null);

  // Redirection si deja connecte (acces direct a /login alors qu'on est connecte)
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async ({ email, password }) => {
    setSubmitting(true);
    setServerError(null);
    try {
      const { claimedProfilId } = await login(email, password);
      if (claimedProfilId) {
        navigate(`/profils/${claimedProfilId}`, {
          replace: true,
          state: { justClaimed: true },
        });
      } else {
        const from = location.state?.from || '/dashboard';
        navigate(from, { replace: true });
      }
    } catch (err) {
      setServerError(mapLoginError(err));
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-md">
      <Link to="/" className="text-ensoi-primary hover:underline">
        ← Retour
      </Link>
      <h1 className="text-3xl font-serif mt-4 mb-6">Connexion</h1>

      <LoginForm
        onSubmit={handleSubmit}
        submitting={submitting}
        serverError={serverError}
      />

      <p className="text-sm text-ensoi-muted mt-6 text-center">
        Pas encore de compte ?{' '}
        <Link to="/register" className="text-ensoi-primary hover:underline font-medium">
          Créer un compte
        </Link>
      </p>
    </div>
  );
}

/**
 * Mappe les erreurs axios en messages utilisateur clairs.
 */
function mapLoginError(err) {
  if (err.code === 'ECONNABORTED') {
    return 'Le serveur met trop de temps à répondre. Réessayez.';
  }
  if (!err.response) {
    return 'Impossible de joindre le serveur. Vérifiez votre connexion.';
  }
  const status = err.response.status;
  if (status === 401) return 'Email ou mot de passe incorrect.';
  if (status === 422) return 'Données invalides, vérifiez vos saisies.';
  if (status === 429) return 'Trop de tentatives. Réessayez dans une minute.';
  if (status >= 500) return 'Erreur du serveur. Réessayez plus tard.';
  return 'Erreur de connexion.';
}
