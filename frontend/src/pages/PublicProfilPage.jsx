import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { profilsApi } from '../api/client';
import CarteNumerologie from '../components/profil/CarteNumerologie';
import CarteCognitif from '../components/profil/CarteCognitif';
import CarteHumanDesign from '../components/profil/CarteHumanDesign';

/**
 * Page d'affichage publique d'un profil partage via un lien.
 *
 * Accessible sans authentification. Le backend retourne le profil
 * SANS la synthese IA (response_model_exclude={'synthese_ia'}).
 *
 * Gere les etats : chargement, lien invalide/expire (404), erreur reseau,
 * profil affiche.
 */
export default function PublicProfilPage() {
  const { token } = useParams();
  const [profil, setProfil] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let annule = false;

    async function chargerProfil() {
      setLoading(true);
      setError(null);
      try {
        const { data } = await profilsApi.public(token);
        if (!annule) {
          setProfil(data);
          setLoading(false);
        }
      } catch (err) {
        if (!annule) {
          setError(err);
          setLoading(false);
        }
      }
    }

    chargerProfil();
    return () => {
      annule = true;
    };
  }, [token]);

  // Etat de chargement
  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-ensoi-muted">Chargement du profil partage...</p>
      </div>
    );
  }

  // Etat d'erreur
  if (error) {
    const status = error.response?.status;
    let titre, detail;

    if (status === 404) {
      titre = 'Lien invalide ou expire';
      detail = (
        "Ce lien de partage n'est plus valide. Il a peut-etre expire " +
        "(les liens sont valables 30 jours) ou a ete revoque par son auteur."
      );
    } else if (!error.response) {
      titre = 'Impossible de joindre le serveur';
      detail = 'Verifiez votre connexion internet et reessayez.';
    } else {
      titre = 'Impossible de charger le profil';
      detail = 'Une erreur est survenue. Veuillez reessayer plus tard.';
    }

    return (
      <div className="container mx-auto p-6 max-w-2xl">
        <Link to="/" className="text-ensoi-primary hover:underline">
          Retour a l'accueil
        </Link>
        <h1 className="text-2xl font-serif mt-4 mb-2">{titre}</h1>
        <p className="text-ensoi-muted">{detail}</p>
      </div>
    );
  }

  // Etat normal : profil affiche
  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <Link to="/" className="text-ensoi-primary hover:underline">
        Retour a l'accueil
      </Link>

      {/* Bandeau d'information : profil partage */}
      <div className="mt-4 mb-6 bg-ensoi-light border border-ensoi-secondary rounded p-4">
        <p className="text-sm text-ensoi-dark">
          <strong>Profil partage par {profil.prenom} {profil.nom_famille}.</strong>
          {' '}Vous consultez une version publique : la synthese personnelle
          n'est pas incluse.
        </p>
      </div>

      <h1 className="text-3xl font-serif mb-1">
        Profil de {profil.prenom} {profil.nom_famille}
      </h1>
      <p className="text-ensoi-muted mb-8">
        Genere le {new Date(profil.created_at).toLocaleDateString('fr-FR', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        })}
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CarteNumerologie numerologie={profil.numerologie} />
        <CarteCognitif cognitif={profil.profil_cognitif} />
        <CarteHumanDesign humanDesign={profil.human_design} />
      </div>

      {/* Pas de BlocSynthese ici : le backend ne renvoie pas la synthese */}
    </div>
  );
}
