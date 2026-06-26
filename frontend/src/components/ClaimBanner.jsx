import { Link } from 'react-router-dom';

/**
 * Banniere qui invite a sauvegarder un profil anonyme.
 *
 * S'affiche en haut de ProfilPage uniquement si :
 * - L'utilisateur n'est pas connecte
 * - Le profil affiche correspond a un claim en attente en sessionStorage
 *
 * CTA principal : creer un compte (la plupart des visiteurs anonymes n'en
 * ont pas, sinon ils seraient deja connectes). CTA secondaire : se connecter.
 *
 * Apres inscription/connexion, le AuthContext consomme automatiquement le
 * claim et l'utilisateur est redirige sur ce meme profil (scenario 3).
 */
export default function ClaimBanner() {
  return (
    <div className="bg-ensoi-primary/10 border border-ensoi-primary/30 rounded-lg p-4 mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div>
        <p className="font-medium text-ensoi-primary">
          Sauvegardez ce profil
        </p>
        <p className="text-sm text-ensoi-muted mt-1">
          Créez un compte pour le retrouver dans votre historique. Sans compte, ce profil sera perdu à la fermeture de l'onglet.
        </p>
      </div>
      <div className="flex gap-2 shrink-0">
        <Link to="/login" className="btn-secondary text-sm">
          J'ai déjà un compte
        </Link>
        <Link to="/register" className="btn-primary text-sm">
          Créer un compte
        </Link>
      </div>
    </div>
  );
}
