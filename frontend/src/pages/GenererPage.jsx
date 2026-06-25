import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { profilsApi } from '../api/client';
import ProfilForm from '../components/ProfilForm';

function formaterErreur(err) {
  if (err.code === 'ECONNABORTED') {
    return {
      titre: 'Le serveur met trop de temps a repondre',
      detail: "Reessayez dans quelques instants. Si le probleme persiste, le serveur est peut-etre temporairement surcharge.",
    };
  }

  if (!err.response) {
    return {
      titre: 'Impossible de joindre le serveur',
      detail: 'Verifiez votre connexion internet et reessayez.',
    };
  }

  const status = err.response.status;

  if (status === 429) {
    return {
      titre: 'Trop de tentatives',
      detail: "Pour eviter la surcharge, la generation est limitee a 3 par minute. Patientez un instant avant de reessayer.",
    };
  }

  if (status === 422) {
    return {
      titre: 'Donnees invalides',
      detail: "Verifiez vos informations (orthographe du nom, date, fuseau horaire) et reessayez.",
    };
  }

  if (status >= 500) {
    return {
      titre: 'Erreur du serveur',
      detail: "Une erreur est survenue cote serveur. Reessayez dans quelques instants.",
    };
  }

  return {
    titre: 'Une erreur est survenue',
    detail: "Veuillez reessayer. Si le probleme persiste, contactez le support.",
  };
}

export default function GenererPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [erreur, setErreur] = useState(null);

  async function handleSubmit(formData) {
    setSubmitting(true);
    setErreur(null);

    const payload = {
      prenom: formData.prenom,
      nom_famille: formData.nom_famille,
      date_naissance: formData.date_naissance,
      reponses_cognitif: formData.reponses_cognitif,
    };
    if (formData.heure_naissance) payload.heure_naissance = formData.heure_naissance;
    if (formData.pays_naissance) payload.pays_naissance = formData.pays_naissance;
    if (formData.fuseau_horaire_naissance) {
      payload.fuseau_horaire_naissance = formData.fuseau_horaire_naissance;
    }

    try {
      const { data } = await profilsApi.generate(payload);
      navigate(`/profils/${data.id}`);
    } catch (err) {
      setErreur(formaterErreur(err));
      setSubmitting(false);
    }
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-serif mb-6">Generer un profil</h1>

      {erreur && (
        <div className="max-w-2xl mx-auto mb-4 p-4 border border-red-300 bg-red-50 rounded">
          <p className="text-red-700 font-medium">{erreur.titre}</p>
          <p className="text-sm text-red-600 mt-1">{erreur.detail}</p>
        </div>
      )}

      <ProfilForm onSubmit={handleSubmit} submitting={submitting} />
    </div>
  );
}
