import { useState } from 'react';
import Step1Infos from './Step1Infos';
import Step2HumanDesign from './Step2HumanDesign';

/**
 * Wizard de génération de profil en 3 étapes.
 *
 * Étape 1 — Informations personnelles (prénom, nom de famille, date)
 * Étape 2 — Données Human Design optionnelles (heure, pays, fuseau)
 * Étape 3 — Questionnaire cognitif (12 curseurs)
 *
 * État détenu par ce composant. À la dernière étape, le parent reçoit
 * les données via onSubmit (props) pour appeler /api/generate.
 *
 * Props :
 *   - onSubmit: (formData) => void — appelé au clic sur "Générer" à l'étape 3
 *   - submitting: boolean — désactive le bouton final pendant l'appel API
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
  const [errors, setErrors] = useState({});

  const totalSteps = 3;

  // Met à jour un champ du formulaire et efface son erreur s'il y en avait une.
  function updateField(name, value) {
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  }

  /**
   * Validation d'un champ individuel.
   * Reflète exactement la validation Pydantic du backend (ProfilRequest) :
   *   - prenom/nom_famille : 1-100 chars, regex lettres+accents+espaces+tirets
   *   - date_naissance : non vide, pas dans le futur
   */
  function validerChamp(name, value) {
    const regexNom = /^[a-zA-ZÀ-ÿ \-]+$/;

    switch (name) {
      case 'prenom':
      case 'nom_famille':
        if (!value || value.trim() === '') {
          return 'Ce champ est obligatoire.';
        }
        if (value.length > 100) {
          return 'Maximum 100 caractères.';
        }
        if (!regexNom.test(value)) {
          return 'Lettres, accents, espaces et tirets uniquement.';
        }
        return undefined;

      case 'date_naissance':
        if (!value) {
          return 'Ce champ est obligatoire.';
        }
        if (new Date(value) > new Date()) {
          return 'La date ne peut pas être dans le futur.';
        }
        return undefined;

      default:
        return undefined;
    }
  }

  // Valide un champ au blur et met l'erreur à jour.
  function handleBlur(name) {
    const erreur = validerChamp(name, formData[name]);
    setErrors((prev) => ({ ...prev, [name]: erreur }));
  }

  // Valide tous les champs requis de l'étape courante.
  function etapeValide() {
    if (step === 1) {
      const champs = ['prenom', 'nom_famille', 'date_naissance'];
      return champs.every((c) => !validerChamp(c, formData[c]));
    }
    // TODO commits 3 et 4 : valider les étapes 2 et 3.
    return true;
  }

  function canGoNext() {
    return etapeValide();
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

      {/* Contenu de l'étape */}
      <div className="min-h-[300px]">
        {step === 1 && (
          <Step1Infos
            values={formData}
            onChange={updateField}
            errors={errors}
            onBlur={handleBlur}
          />
        )}

        {step === 2 && (
  <Step2HumanDesign
    values={formData}
    onChange={updateField}
  />
)}

        {step === 3 && (
          <div>
            <h2 className="text-2xl font-serif mb-4">Questionnaire cognitif</h2>
            <p className="text-ensoi-muted">
              [À implémenter au commit 4 — 12 curseurs via CognitiveQuestionnaire]
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
