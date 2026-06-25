import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { profilsApi } from '../api/client';

export default function ProfilPage() {
  const { id } = useParams();
  const [profil, setProfil] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let annule = false;

    async function chargerProfil() {
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
    return (
      <div className="container mx-auto p-6">
        <Link to="/" className="text-ensoi-primary hover:underline">
          Retour
        </Link>
        <h1 className="text-2xl font-serif mt-4 mb-2">
          {status === 404 ? 'Profil introuvable' : 'Impossible de charger le profil'}
        </h1>
        <p className="text-ensoi-muted">
          {status === 404
            ? "Ce profil n'existe pas ou a ete supprime."
            : "Veuillez reessayer plus tard."}
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <Link to="/" className="text-ensoi-primary hover:underline">
        Retour
      </Link>
      <p className="text-ensoi-muted mb-6">
        Genere le {new Date(profil.created_at).toLocaleString('fr-FR', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })}
      </p>
      <p className="text-ensoi-muted mb-6">
        Genere le {new Date(profil.created_at).toLocaleDateString('fr-FR')}
      </p>

      {profil.statut === 'partiel' && (
        <div className="mb-6 p-4 border border-amber-300 bg-amber-50 rounded">
          <p className="text-amber-800">
            La synthese IA n'est pas disponible pour ce profil. Les calculs
            de numerologie, profil cognitif et Human Design sont complets.
          </p>
        </div>
      )}

      <details className="mt-6">
        <summary className="cursor-pointer text-sm text-ensoi-muted">
          Voir les donnees brutes du profil (debug temporaire)
        </summary>
        <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto">
          {JSON.stringify(profil, null, 2)}
        </pre>
      </details>
    </div>
  );
}
