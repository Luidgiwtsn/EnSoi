import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { profilsApi } from '../api/client';
import ProfilForm from '../components/ProfilForm';

// Page d'orchestration du wizard de generation de profil.
//
// Flux :
//   1. L'utilisateur remplit le wizard ProfilForm
//   2. Au submit, on appelle POST /api/generate avec le payload complet
//   3. Le backend renvoie le profil cree (avec son id)
//   4. On redirige vers /profils/:id
//
// La gestion fine des erreurs (429, 422, 503) sera affinee au commit 8.

export default function GenererPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(formData) {
    setSubmitting(true);
    setError(null);

    // Prepare le payload : on n'envoie au backend que les champs renseignes.
    // Pydantic accepte l'absence des cles optionnelles, mais une chaine vide
    // pour pays_naissance ferait echouer la validation pycountry.
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
      setError(err);
      setSubmitting(false);
    }
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-serif mb-6">Generer un profil</h1>

      {error && (
        <div className="max-w-2xl mx-auto mb-4 p-4 border border-red-300 bg-red-50 rounded">
          <p className="text-red-700 font-medium">
            Une erreur est survenue lors de la generation.
          </p>
          <p className="text-sm text-red-600 mt-1">
            Veuillez reessayer. Si le probleme persiste, contactez le support.
          </p>
        </div>
      )}

      <ProfilForm onSubmit={handleSubmit} submitting={submitting} />
    </div>
  );
}
