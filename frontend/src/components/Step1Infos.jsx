import { useState } from 'react';

/**
 * Étape 1 du wizard ProfilForm - informations personnelles.
 *
 * Champs : prénom, nom de famille, date de naissance.
 * Validation au blur (quand l'utilisateur quitte le champ).
 * Reflète la validation backend (regex + max_length + date non future).
 *
 * Props :
 *   - values: { prenom, nom_famille, date_naissance }
 *   - onChange: (champ, valeur) => void
 *   - errors: { prenom?, nom_famille?, date_naissance? } - pilotées par le parent
 *   - onBlur: (champ) => void - déclenche la validation pour ce champ
 */
export default function Step1Infos({ values, onChange, errors, onBlur }) {
  return (
    <div>
      <h2 className="text-2xl font-serif mb-6">Vos informations</h2>

      <div className="space-y-4">
        <Field
          label="Prénom"
          name="prenom"
          value={values.prenom}
          onChange={onChange}
          onBlur={onBlur}
          error={errors.prenom}
          placeholder="Marie"
          autoComplete="given-name"
          required
        />

        <Field
          label="Nom de famille"
          name="nom_famille"
          value={values.nom_famille}
          onChange={onChange}
          onBlur={onBlur}
          error={errors.nom_famille}
          placeholder="Dupont"
          autoComplete="family-name"
          required
        />

        <Field
          label="Date de naissance"
          name="date_naissance"
          type="date"
          value={values.date_naissance}
          onChange={onChange}
          onBlur={onBlur}
          error={errors.date_naissance}
          max={new Date().toISOString().split('T')[0]} // pas de date future
          required
        />
      </div>
    </div>
  );
}

/**
 * Petit composant interne pour factoriser un champ avec label + erreur.
 */
function Field({ label, name, value, onChange, onBlur, error, type = 'text', ...rest }) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium mb-1">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={(e) => onChange(name, e.target.value)}
        onBlur={() => onBlur(name)}
        className={`w-full border rounded px-3 py-2 ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
        {...rest}
      />
      {error && (
        <p className="text-sm text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
}
