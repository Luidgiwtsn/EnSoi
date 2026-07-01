import { useState, useEffect } from 'react';
import { profilsApi } from '../api/client';

// Questionnaire cognitif controle.
// Charge les 12 questions depuis le backend et rend 12 curseurs 1 a 5.
// Les questions sont regroupees par axe (Energie, Perception, Decision,
// Organisation) avec un sous-titre au-dessus du premier item du groupe.
//
// Props:
//   value    : (number | null)[12] etat des reponses
//   onChange : (nouvelles_reponses) => void appele a chaque interaction

export default function CognitiveQuestionnaire({ value, onChange }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

    return () => {
      annule = true;
    };
  }, []);

  function handleSliderChange(index, nouvelleValeur) {
    const nouvellesReponses = [...value];
    nouvellesReponses[index] = nouvelleValeur;
    onChange(nouvellesReponses);
  }

  if (loading) {
    return (
      <div className="p-6 text-center text-gray-500">
        Chargement des questions...
      </div>
    );
  }

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
          Reessayer
        </button>
      </div>
    );
  }

  const nbRepondues = value.filter((r) => r !== null).length;

  return (
    <div className="space-y-2">
      <div className="text-sm text-gray-600 mb-4">
        {nbRepondues} / {questions.length} questions répondues
      </div>

      {questions.map((question, index) => {
        const reponse = value[index];
        const repondue = reponse !== null;
        const premierDeLaxe = index === 0 || questions[index - 1].axe !== question.axe;

        return (
          <div key={question.id}>
            {premierDeLaxe && (
              <h3 className="text-lg font-serif mt-6 mb-3 text-ensoi-primary">
                {question.axe}
              </h3>
            )}
            <div className="border-b pb-4 mb-3">
              <div className="text-xs uppercase text-gray-500 mb-1">
                Question {index + 1}
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
                  Reponse : {reponse}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
