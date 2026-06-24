import { useState, useEffect } from 'react';
import { profilsApi } from '../api/client';

/**
 * Questionnaire cognitif contrôlé.
 *
 * Charge les 12 questions depuis le backend (source unique de vérité) et
 * rend 12 curseurs 1-5. Le parent détient l'état des réponses.
 *
 * Props:
 *   - value: (number | null)[] de longueur 12 — état des réponses
 *   - onChange: (nouvelles_reponses) => void — appelé à chaque interaction
 */
export default function CognitiveQuestionnaire({ value, onChange }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Récupère les questions au montage et à chaque tentative de rechargement.
  useEffect(() => {
    let annule = false;

    async function chargerQuestions() {
      setLoading(true);
      setError(null);
      try {
        const { data } = await profilsApi.cognitif();
        if (!annule) {
          setQuestions(data.questions);
          setLoading(false);
        }
      } catch (err) {
        if (!annule) {
          setError(err);
          setLoading(false);
        }
      }
    }

    chargerQuestions();

    // Nettoyage : si le composant se démonte avant la fin du fetch,
    // on évite de mettre à jour un état qui n'existe plus.
    return () => {
      annule = true;
    };
  }, []);

  // Met à jour une réponse précise sans muter le tableau existant.
  function handleSliderChange(index, nouvelleValeur) {
    const nouvellesReponses = [...value];
    nouvellesReponses[index] = nouvelleValeur;
    onChange(nouvellesReponses);
  }

  // --- Rendu conditionnel : loading ---
  if (loading) {
    return (
      <div className="p-6 text-center text-gray-500">
        Chargement des questions…
      </div>
    );
  }

  // --- Rendu conditionnel : erreur ---
  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-red-600 mb-3">
          Impossible de charger les questions.
        </p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Réessayer
        </button>
      </div>
    );
  }

  // --- Rendu principal : les 12 questions ---
  const nbRepondues = value.filter((r) => r !== null).length;

  return (
    <div className="space-y-6">
      <div className="text-sm text-gray-600">
        {nbRepondues} / {questions.length} questions répondues
      </div>

      {questions.map((question, index) => {
        const reponse = value[index];
        const repondue = reponse !== null;

        return (
          <div key={question.id} className="border-b pb-4">
            <div className="text-xs uppercase text-gray-500 mb-1">
              Question {index + 1} — Axe : {question.axe}
            </div>
            <p className="font-medium mb-3">{question.texte}</p>

            <input
              type="range"
              min={1}
              max={5}
              step={1}
              value={reponse ?? 3}
              onChange={(e) =>
                handleSliderChange(index, Number(e.target.value))
              }
              className={`w-full ${repondue ? 'opacity-100' : 'opacity-40'}`}
            />

            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>{question.pole_a}</span>
              <span>{question.pole_b}</span>
            </div>

            {repondue && (
              <div className="text-center text-sm mt-1 text-blue-600">
                Réponse : {reponse}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
