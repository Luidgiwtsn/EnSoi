import { useState, useEffect } from 'react';
import { profilsApi } from '../api/client';

/**
 * Étape 2 du wizard ProfilForm - données Human Design optionnelles.
 *
 * Champs : heure de naissance, pays de naissance, fuseau horaire.
 * Tous optionnels - l'utilisateur peut tout laisser vide. Si tous sont
 * renseignés, le calcul Human Design est plus précis (donnees_completes=true
 * côté backend).
 *
 * Les listes pays et fuseaux sont chargées via les endpoints backend
 * (source unique de vérité, alignée avec la validation pycountry/pytz).
 * Les fuseaux sont groupés par continent via <optgroup> pour la lisibilité.
 *
 * Props :
 *   - values: { heure_naissance, pays_naissance, fuseau_horaire_naissance }
 *   - onChange: (champ, valeur) => void
 */
export default function Step2HumanDesign({ values, onChange }) {
  const [countries, setCountries] = useState([]);
  const [timezones, setTimezones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Chargement parallèle des deux listes au montage.
  useEffect(() => {
    let annule = false;

    async function chargerListes() {
      setLoading(true);
      setError(null);
      try {
        const [resCountries, resTimezones] = await Promise.all([
          profilsApi.countries(),
          profilsApi.timezones(),
        ]);
        if (!annule) {
          setCountries(resCountries.data.countries);
          setTimezones(resTimezones.data.timezones);
          setLoading(false);
        }
      } catch (err) {
        if (!annule) {
          setError(err);
          setLoading(false);
        }
      }
    }

    chargerListes();

    return () => {
      annule = true;
    };
  }, []);

  // Regroupe les fuseaux par préfixe (Africa/, Europe/, etc.) pour <optgroup>.
  // Les fuseaux sans "/" (UTC, GMT) sont placés dans un groupe "Autres".
  function grouperFuseaux(liste) {
    const groupes = {};
    for (const tz of liste) {
      const prefix = tz.includes('/') ? tz.split('/')[0] : 'Autres';
      if (!groupes[prefix]) groupes[prefix] = [];
      groupes[prefix].push(tz);
    }
    return groupes;
  }

  if (loading) {
    return (
      <div>
        <h2 className="text-2xl font-serif mb-6">Données Human Design</h2>
        <p className="text-ensoi-muted">Chargement des listes…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h2 className="text-2xl font-serif mb-6">Données Human Design</h2>
        <p className="text-red-600 mb-3">
          Impossible de charger les listes de pays et fuseaux.
        </p>
        <p className="text-sm text-ensoi-muted">
          Vous pouvez quand même continuer sans ces informations. Cliquez sur "Suivant →".
        </p>
      </div>
    );
  }

  const groupesFuseaux = grouperFuseaux(timezones);

  return (
    <div>
      <h2 className="text-2xl font-serif mb-2">Données Human Design</h2>
      <p className="text-sm text-ensoi-muted mb-6">
        Ces informations sont <strong>optionnelles</strong>. Si vous les
        renseignez, le calcul Human Design sera plus précis. Sinon, vous
        pouvez passer cette étape sans rien remplir.
      </p>

      <div className="space-y-4">
        <div>
          <label htmlFor="heure_naissance" className="block text-sm font-medium mb-1">
            Heure de naissance
          </label>
          <input
            id="heure_naissance"
            name="heure_naissance"
            type="time"
            value={values.heure_naissance}
            onChange={(e) => onChange('heure_naissance', e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="pays_naissance" className="block text-sm font-medium mb-1">
            Pays de naissance
          </label>
          <select
            id="pays_naissance"
            name="pays_naissance"
            value={values.pays_naissance}
            onChange={(e) => onChange('pays_naissance', e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          >
            <option value="">— Non renseigné —</option>
            {countries.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="fuseau_horaire_naissance" className="block text-sm font-medium mb-1">
            Fuseau horaire de naissance
          </label>
          <select
            id="fuseau_horaire_naissance"
            name="fuseau_horaire_naissance"
            value={values.fuseau_horaire_naissance}
            onChange={(e) => onChange('fuseau_horaire_naissance', e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          >
            <option value="">— Non renseigné —</option>
            {Object.entries(groupesFuseaux).map(([continent, fuseaux]) => (
              <optgroup key={continent} label={continent}>
                {fuseaux.map((tz) => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
