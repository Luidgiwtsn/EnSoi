import { useState } from 'react';

/**
 * Wizard de génération de profil en 3 étapes.
 *
 * Étape 1 - Informations personnelles (prénom, nom de famille, date)
 * Étape 2 - Données Human Design optionnelles (heure, pays, fuseau)
 * Étape 3 - Questionnaire cognitif (12 curseurs)
 *
 * État détenu par ce composant. À la dernière étape, le parent reçoit
 * les données via onSubmit (props) pour appeler /api/generate.
 *
 * Props :
 *   - onSubmit: (formData) => void - appelé au clic sur "Générer" à l'étape 3
 *   - submitting: boolean - désactive le bouton final pendant l'appel API
 */
export default function ProfilForm({ onSubmit, submitting = false }) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    prenom: '',
    nom_famille: '',
    date_naissance: '',
    heure_naissance: '',
    pays_naissance: '',
    fuseau_horaire_naissance: '',
    reponses_cognitif: Array(12).fill(null),
  });

  const totalSteps = 3;

  // TODO commits 2/3/4 : ajouter une vraie validation par étape.
  // Pour l'instant on autorise la navigation libre pour tester le squelette.
  function canGoNext() {
    return true;
  }

  function handleNext() {
    if (canGoNext() && step < totalSteps) {
      setStep(step + 1);
    }
  }

  function handlePrevious() {
    if (step > 1) {
      setStep(step - 1);
    }
  }

  function handleSubmit() {
    if (canGoNext()) {
      onSubmit(formData);
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Barre de progression */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-ensoi-muted mb-2">
          <span>Étape {step} sur {totalSteps}</span>
          <span>{Math.round((step / totalSteps) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-ensoi-primary h-2 rounded-full transition-all"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      {/* Contenu de l'étape — placeholders pour ce commit */}
      <div className="min-h-[300px]">
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-serif mb-4">Vos informations</h2>
            <p className="text-ensoi-muted">
              [À implémenter au commit 2 - prénom, nom de famille, date de naissance]
            </p>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-2xl font-serif mb-4">Données Human Design (optionnel)</h2>
            <p className="text-ensoi-muted">
              [À implémenter au commit 3 - heure, pays, fuseau horaire]
            </p>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="text-2xl font-serif mb-4">Questionnaire cognitif</h2>
            <p className="text-ensoi-muted">
              [À implémenter au commit 4 - 12 curseurs via CognitiveQuestionnaire]
            </p>
          </div>
        )}
      </div>

      {/* Boutons de navigation */}
      <div className="flex justify-between mt-8">
        <button
          type="button"
          onClick={handlePrevious}
          disabled={step === 1}
          className="btn-secondary disabled:opacity-40 disabled:cursor-not-allowed"
        >
          ← Précédent
        </button>

        {step < totalSteps ? (
          <button
            type="button"
            onClick={handleNext}
            disabled={!canGoNext()}
            className="btn-primary disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Suivant →
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canGoNext() || submitting}
            className="btn-primary disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {submitting ? 'Génération…' : 'Générer mon profil'}
          </button>
        )}
      </div>
    </div>
  );
}
