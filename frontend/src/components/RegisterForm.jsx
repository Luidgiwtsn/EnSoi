import { useState } from 'react';

/**
 * Formulaire d'inscription - composant controle.
 *
 * Validation client miroir du backend :
 * - prenom / nom_famille : ^[a-zA-ZÀ-ÿ \-]+$, max 100 chars
 * - email : format basique
 * - password : min 8 chars, au moins 1 majuscule et 1 chiffre
 * - confirmation_password : doit matcher password
 * - date_naissance : pas dans le futur
 *
 * Props :
 * - onSubmit({ prenom, nom_famille, email, password, date_naissance })
 * - submitting : desactive le formulaire pendant l'appel API
 * - serverError : message global (ex: "Un compte existe deja avec cet email")
 */
const NAME_PATTERN = /^[a-zA-ZÀ-ÿ \-]+$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function RegisterForm({ onSubmit, submitting = false, serverError = null }) {
  const [form, setForm] = useState({
    prenom: '',
    nom_famille: '',
    email: '',
    password: '',
    confirmPassword: '',
    date_naissance: '',
  });
  const [errors, setErrors] = useState({});

  const update = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value });
  };

  const validate = () => {
    const e = {};

    if (!form.prenom.trim()) e.prenom = 'Le prénom est requis';
    else if (form.prenom.length > 100) e.prenom = 'Maximum 100 caractères';
    else if (!NAME_PATTERN.test(form.prenom))
      e.prenom = 'Lettres, espaces et tirets uniquement';

    if (!form.nom_famille.trim()) e.nom_famille = 'Le nom est requis';
    else if (form.nom_famille.length > 100) e.nom_famille = 'Maximum 100 caractères';
    else if (!NAME_PATTERN.test(form.nom_famille))
      e.nom_famille = 'Lettres, espaces et tirets uniquement';

    if (!form.email.trim()) e.email = "L'email est requis";
    else if (!EMAIL_PATTERN.test(form.email)) e.email = "Format d'email invalide";

    if (!form.password) e.password = 'Le mot de passe est requis';
    else if (form.password.length < 8) e.password = 'Minimum 8 caractères';
    else if (!/[A-Z]/.test(form.password))
      e.password = 'Au moins une majuscule requise';
    else if (!/[0-9]/.test(form.password))
      e.password = 'Au moins un chiffre requis';

    if (form.confirmPassword !== form.password)
      e.confirmPassword = 'Les mots de passe ne correspondent pas';

    if (!form.date_naissance) e.date_naissance = 'La date de naissance est requise';
    else if (new Date(form.date_naissance) > new Date())
      e.date_naissance = 'La date ne peut pas être dans le futur';

    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (ev) => {
    ev.preventDefault();
    if (validate()) {
      onSubmit({
        prenom: form.prenom.trim(),
        nom_famille: form.nom_famille.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        date_naissance: form.date_naissance,
      });
    }
  };

  const inputClass =
    'w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ensoi-primary';

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="prenom" className="block text-sm font-medium mb-1">
            Prénom
          </label>
          <input
            id="prenom"
            type="text"
            autoComplete="given-name"
            value={form.prenom}
            onChange={update('prenom')}
            onBlur={validate}
            disabled={submitting}
            className={inputClass}
          />
          {errors.prenom && (
            <p className="text-red-600 text-sm mt-1">{errors.prenom}</p>
          )}
        </div>

        <div>
          <label htmlFor="nom_famille" className="block text-sm font-medium mb-1">
            Nom de famille
          </label>
          <input
            id="nom_famille"
            type="text"
            autoComplete="family-name"
            value={form.nom_famille}
            onChange={update('nom_famille')}
            onBlur={validate}
            disabled={submitting}
            className={inputClass}
          />
          {errors.nom_famille && (
            <p className="text-red-600 text-sm mt-1">{errors.nom_famille}</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          value={form.email}
          onChange={update('email')}
          onBlur={validate}
          disabled={submitting}
          className={inputClass}
        />
        {errors.email && (
          <p className="text-red-600 text-sm mt-1">{errors.email}</p>
        )}
      </div>

      <div>
        <label htmlFor="date_naissance" className="block text-sm font-medium mb-1">
          Date de naissance
        </label>
        <input
          id="date_naissance"
          type="date"
          autoComplete="bday"
          value={form.date_naissance}
          onChange={update('date_naissance')}
          onBlur={validate}
          disabled={submitting}
          max={new Date().toISOString().split('T')[0]}
          className={inputClass}
        />
        {errors.date_naissance && (
          <p className="text-red-600 text-sm mt-1">{errors.date_naissance}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">
          Mot de passe
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          value={form.password}
          onChange={update('password')}
          onBlur={validate}
          disabled={submitting}
          className={inputClass}
        />
        {errors.password ? (
          <p className="text-red-600 text-sm mt-1">{errors.password}</p>
        ) : (
          <p className="text-ensoi-muted text-xs mt-1">
            Minimum 8 caractères, avec au moins une majuscule et un chiffre.
          </p>
        )}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1">
          Confirmation du mot de passe
        </label>
        <input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          value={form.confirmPassword}
          onChange={update('confirmPassword')}
          onBlur={validate}
          disabled={submitting}
          className={inputClass}
        />
        {errors.confirmPassword && (
          <p className="text-red-600 text-sm mt-1">{errors.confirmPassword}</p>
        )}
      </div>

      {serverError && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded px-3 py-2 text-sm">
          {serverError}
        </div>
      )}

      <button
        type="submit"
        disabled={submitting}
        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {submitting ? 'Création en cours...' : 'Créer mon compte'}
      </button>
    </form>
  );
}
