import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { profilsApi, pendingClaimStore } from '../api/client';
import { useAuth } from '../hooks/useAuth';
import CarteNumerologie from '../components/profil/CarteNumerologie';
import CarteCognitif from '../components/profil/CarteCognitif';
import CarteHumanDesign from '../components/profil/CarteHumanDesign';
import BlocSynthese from '../components/profil/BlocSynthese';
import ClaimBanner from '../components/ClaimBanner';

export default function ProfilPage() {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const [profil, setProfil] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Detecte si le profil affiche correspond a un claim en attente en sessionStorage.
  // Si oui ET que l'utilisateur n'est pas connecte, on affiche la banniere "Sauvegardez ce profil".
  const pending = pendingClaimStore.get();
  const showClaimBanner =
    !isAuthenticated && pending !== null && String(pending.profilId) === String(id);

  useEffect(() => {
    let annule = false;
    async function chargerProfil(){
      setLoading(true);
      setError(null);
      try {
        const { data } = await profilsApi.get(id);
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
  }, [id]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-ensoi-muted">Chargement du profil...</p>
      </div>
    );
  }

  if (error) {
    const status = error.response?.status;
    let titre, detail;
    if (status === 404) {
      titre = 'Profil introuvable';
      detail = "Ce profil n'existe pas ou a ete supprime.";
    } else if (status === 403) {
      titre = 'Acces refuse';
      detail = "Ce profil ne vous appartient pas.";
    } else if (!error.response) {
      titre = 'Impossible de joindre le serveur';
      detail = 'Verifiez votre connexion internet et reessayez.';
    } else {
      titre = 'Impossible de charger le profil';
      detail = 'Veuillez reessayer plus tard.';
    }
    return (
      <div className="container mx-auto p-6">
        <Link to="/" className="text-ensoi-primary hover:underline">
          Retour
        </Link>
        <h1 className="text-2xl font-serif mt-4 mb-2">{titre}</h1>
        <p className="text-ensoi-muted">{detail}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <Link to="/" className="text-ensoi-primary hover:underline">
        Retour
      </Link>
      <h1 className="text-3xl font-serif mt-4 mb-1">
        Profil de {profil.prenom} {profil.nom_famille}
      </h1>
      <p className="text-ensoi-muted mb-8">
        Genere le {new Date(profil.created_at).toLocaleString('fr-FR', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })}
      </p>

      {showClaimBanner && <ClaimBanner />}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <CarteNumerologie numerologie={profil.numerologie} />
        <CarteCognitif cognitif={profil.profil_cognitif} />
        <CarteHumanDesign humanDesign={profil.human_design} />
      </div>
      <BlocSynthese
        synthese={profil.synthese_ia}
        statut={profil.statut}
      />
    </div>
  );
}
