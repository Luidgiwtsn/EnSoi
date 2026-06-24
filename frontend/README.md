# EnSoi — Frontend

Interface utilisateur React de l'application EnSoi. Consomme l'API backend FastAPI.

> Pour la vue d'ensemble du projet, l'architecture et la documentation backend, voir le [README à la racine](../README.md).

---

## 🛠 Stack

| Outil | Version | Rôle |
|-------|---------|------|
| React | 18 | Framework UI |
| Vite | dernière | Build tool + dev server (HMR) |
| Tailwind CSS | 3.4 | Styling utility-first |
| React Router | 6 | Routing client-side |
| axios | dernière | Client HTTP avec intercepteurs |
| jsPDF | dernière | Export PDF côté client (à venir) |

---

##  Démarrage

```bash
npm install
cp .env.example .env       # éditer VITE_API_URL si nécessaire
npm run dev                # → http://localhost:5173
```

Le backend doit tourner sur `http://localhost:8000` (voir le [README racine](../README.md)).

### Build production

```bash
npm run build              # génère dist/
npm run preview            # prévisualiser le build
```

---

##  Structure
src/

├── api/

│   └── client.js          # Client axios avec JWT en mémoire + refresh auto sur 401

├── components/

│   └── ErrorBoundary.jsx  # Capture les erreurs React inattendues

├── hooks/                 # Hooks personnalisés (useAuth à venir)

├── pages/                 # Pages routées par React Router

└── App.jsx                # Routes + ErrorBoundary global

---

##  Sécurité côté client

- **JWT en mémoire uniquement** : jamais stocké dans `localStorage` ou `sessionStorage` (protection contre XSS)
- **Refresh automatique sur 401** : intercepteur axios qui mutualise les refreshs concurrents (un seul appel `/auth/refresh` même si plusieurs requêtes 401 arrivent en même temps)
- **Événement `auth:expired`** : émis par le client quand le refresh échoue définitivement, écouté par le router pour rediriger vers `/login`

---

##  API consommée

Le client `src/api/client.js` expose trois wrappers :

- `authApi` : register, login, refresh, logout, changePassword
- `usersApi` : getMe, updateMe, updateEmail, deleteMe
- `profilsApi` : generate, list, get, delete, share, getPublic, getCognitifQuestions

Voir le [README racine](../README.md) pour la liste complète des endpoints backend et leurs contrats.

---

## 🗺 Roadmap frontend

Branches restantes du sprint 2 :

- `feature/profil-generation-ui` : formulaire + 12 questions cognitives + 3 cartes + synthèse IA
- `feature/auth-ui` : LoginForm, RegisterForm, PrivateRoute
- `feature/dashboard-ui` : historique des profils sauvegardés
- `feature/export-pdf` : génération PDF via jsPDF
- `feature/share-public` : page publique `/public/:token`
- `feature/deployment` : Vercel + QA
