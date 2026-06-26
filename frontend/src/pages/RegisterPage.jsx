import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm';
import { useAuth } from '../hooks/useAuth';

/**
 * Page /register - orchestre le formulaire et le flow d'inscription.
 *
 * Logique :
 * 1. Si deja connecte, redirige vers /dashboard.
 * 2. Sur submit, appelle register() du AuthContext (qui register + login + claim eventuel).
 * 3. Si claim effectue, redirige vers /profils/{id} avec un toast "Profil rattache".
 * 4. Sinon, redirige vers state.from ou /dashboard.
 * 5. Erreurs : 409 = email deja utilise, 400 = regles MDP non respectees, 422, 429, etc.
 */
export default function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (formData) => {
    setSubmitting(true);
    setServerError(null);
    try {
      const { claimedProfilId } = await register(formData);
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
      setServerError(mapRegisterError(err));
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-md">
      <Link to="/" className="text-ensoi-primary hover:underline">
        ← Retour
      </Link>
      <h1 className="text-3xl font-serif mt-4 mb-6">Créer un compte</h1>

      <RegisterForm
        onSubmit={handleSubmit}
        submitting={submitting}
        serverError={serverError}
      />

      <p className="text-sm text-ensoi-muted mt-6 text-center">
        Déjà un compte ?{' '}
        <Link to="/login" className="text-ensoi-primary hover:underline font-medium">
          Se connecter
        </Link>
      </p>
    </div>
  );
}

/**
 * Mappe les erreurs axios en messages utilisateur clairs.
 * Le backend renvoie souvent un detail explicite (ex: "Le mot de passe doit
 * contenir au moins 8 caractères"), qu'on remonte tel quel si pertinent.
 */
function mapRegisterError(err) {
  if (err.code === 'ECONNABORTED') {
    return 'Le serveur met trop de temps à répondre. Réessayez.';
  }
  if (!err.response) {
    return 'Impossible de joindre le serveur. Vérifiez votre connexion.';
  }
  const status = err.response.status;
  const backendDetail = err.response.data?.detail;

  if (status === 409) return 'Un compte existe déjà avec cet email.';
  if (status === 400 && typeof backendDetail === 'string') return backendDetail;
  if (status === 422) {
    // Pydantic renvoie un array de details ; on prend le premier message
    if (Array.isArray(backendDetail) && backendDetail[0]?.msg) {
      return backendDetail[0].msg;
    }
    return 'Données invalides, vérifiez les champs.';
  }
  if (status === 429) return 'Trop de tentatives. Réessayez dans une minute.';
  if (status >= 500) return 'Erreur du serveur. Réessayez plus tard.';
  return "Erreur lors de la création du compte.";
}
