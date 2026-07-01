# EnSoi

> Application web fullstack de développement personnel assistée par IA.

EnSoi génère un profil personnalisé à partir du prénom, nom de famille et date de naissance d'un utilisateur, en combinant trois systèmes complémentaires (numérologie, profil cognitif, Human Design) synthétisés par un LLM via l'API Groq.

---

##  Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | FastAPI 0.115 (Python 3.11+) |
| ORM | SQLModel |
| Base de données | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Rate limiting | slowapi |
| IA | Groq SDK + LLaMA 3.3 70B versatile |
| Frontend | React 18 + Vite + Tailwind CSS |
| Export PDF | jsPDF (côté client) |
| CI | GitHub Actions |
| Déploiement backend | Railway |
| Déploiement frontend | Vercel |

---

##  Architecture
Utilisateur (navigateur)

│

▼

Frontend React (Vercel)

│ REST API / JSON

▼

Backend FastAPI (Railway)

├── Services métier : NumerologieService · HumanDesignService · ProfilCognitifService

├── Auth : AuthService (JWT + bcrypt)

└── IA : GroqService (LLaMA 3.3 / CO-STAR)

│ SQL                         │ HTTP (timeout 8s)

▼                             ▼

PostgreSQL                     Groq API (externe)

---

##  Démarrage rapide

### Prérequis

- Python 3.11+
- Node.js 18+
- PostgreSQL 16
- Une clé API Groq (gratuite sur https://console.groq.com)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Éditer .env et renseigner DATABASE_URL, SECRET_KEY, GROQ_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- API : http://localhost:8000
- Documentation interactive Swagger : http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

- Interface : http://localhost:5173

### Tests

```bash
cd backend
pytest                              # tous les tests (184 actuellement)
pytest --cov=app --cov-report=html  # avec couverture
```

---

##  Déploiement

L'application est déployée sur deux services :
- **Backend + PostgreSQL** : Railway
- **Frontend** : Vercel

### Backend sur Railway

1. Créer un projet Railway, lier le repo GitHub `EnSoi`.
2. Dans les settings du service backend, définir **Root Directory** = `backend`.
3. Ajouter un service PostgreSQL au projet (Railway l'injecte automatiquement via `${{Postgres.DATABASE_URL}}`).
4. Configurer les variables d'environnement (voir `backend/.env.example` pour la liste complète) :

| Variable | Valeur prod |
|----------|-------------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (injecté par Railway) |
| `SECRET_KEY` | Générer avec `python -c "import secrets; print(secrets.token_hex(32))"` — clé différente du dev |
| `GROQ_API_KEY` | Clé Groq de production |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `FRONTEND_URLS` | URL Vercel (ex: `https://ensoi.vercel.app`) |
| `ENVIRONMENT` | `production` |
| `RAILPACK_DEPLOY_APT_PACKAGES` | `libsqlite3-0` (requis par pyswisseph pour les calculs Human Design) |

> **Note** : `RAILPACK_DEPLOY_APT_PACKAGES` est une variable de **build Railway** (pas d'application). Elle n'a pas d'équivalent local et n'apparaît donc pas dans `backend/.env.example`. Elle indique à Railpack d'installer le paquet apt `libsqlite3-0`, nécessaire au runtime de `pyswisseph` (Swiss Ephemeris).


5. Au démarrage, le `Procfile` exécute `alembic upgrade head` puis lance Uvicorn — les migrations sont donc appliquées automatiquement à chaque déploiement.
6. Vérifier la santé après déploiement : `curl https://<URL-RAILWAY>/api/health`.

### Frontend sur Vercel

1. Créer un projet Vercel, lier le repo GitHub `EnSoi`.
2. Dans les settings, définir **Root Directory** = `frontend`.
3. Vercel détecte automatiquement Vite (`npm install` + `npm run build`, output `dist/`).
4. Configurer la variable d'environnement :

| Variable | Valeur prod |
|----------|-------------|
| `VITE_API_URL` | URL Railway du backend (ex: `https://ensoi-backend.up.railway.app`) |

5. Le `vercel.json` à la racine du frontend gère :
   - Le routing SPA (toutes les routes servent `index.html`, React Router prend le relais)
   - Les headers de sécurité (HSTS, X-Frame-Options, Referrer-Policy, etc.)

### Workflow

Chaque `git push` sur `main` déclenche un redéploiement automatique des deux services. Pour un déploiement de test, créer une branche `staging` et configurer un environnement de preview côté Railway/Vercel.

---

##  Endpoints API

### Auth (publics)

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/auth/register` | Inscription (rate-limit : 5/min) |
| POST | `/auth/login` | Connexion (rate-limit : 5/min) |
| POST | `/auth/refresh` | Renouveler l'access token |
| POST | `/auth/logout` | Déconnexion + invalidation refresh token |
| POST | `/auth/change-password` |  Changer le mot de passe |

Le `body` d'inscription attend : `{prenom, nom_famille, email, password, date_naissance}`.

### Users ( authentifiés)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/users/me` | Récupérer ses infos |
| PATCH | `/users/me` | Modifier prenom, nom_famille ou date_naissance |
| PATCH | `/users/me/email` | Modifier son email (mot de passe requis) |
| DELETE | `/users/me` | Supprimer son compte (cascade sur profils) |

### Profils

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/generate` | Générer un profil (rate-limit : 3/min) |
| GET | `/api/profils` |  Liste de ses profils sauvegardés |
| GET | `/api/profils/{id}` | Détail d'un profil |
| DELETE | `/api/profils/{id}` |  Supprimer un profil |
| POST | `/api/profils/{id}/share` |  Générer un lien public (30 jours) |
| GET | `/public/{token}` | Profil partagé public |
| GET | `/api/cognitif/questions` | Les 12 questions du questionnaire cognitif |
| GET | `/api/health` | Health check (BDD + Groq) |

---

##  Règles de sécurité

- **Mot de passe** : minimum 8 caractères, au moins 1 majuscule et 1 chiffre
- **Noms** : pattern `^[a-zA-ZÀ-ÿ \-]+$` (lettres, accents, espaces simples, tirets), 1 à 100 caractères
- **JWT** : access token 30 min + refresh token 7 jours (hashé en BDD)
- **bcrypt** : work factor 12, salt automatique
- **Rate limiting** : 5/min sur `/auth/login`, 3/min sur `/api/generate`
- **CORS** : restreint à `FRONTEND_URL`
- **Prompt injection** : séparation données/instructions dans le prompt CO-STAR de Groq

---

##  Tests

184 tests pytest organisés par module :
test_numerologie.py      - 16 tests (algorithme)

test_human_design.py     - 46 tests (moteur Swiss Ephemeris)

test_profil_cognitif.py  - 13 tests (questionnaire)

test_groq_service.py     - 14 tests (mocks + circuit breaker)

test_auth.py             - 23 tests (JWT, bcrypt, flux complet)

test_api_generate.py     - 19 tests (POST /api/generate + CRUD)

test_api_cognitif.py     -  6 tests (GET /api/cognitif/questions)

test_rate_limiting.py    -  5 tests (slowapi actif)

test_input_validation.py - 42 tests (patterns regex + max_length)

GitHub Actions exécute `pytest` sur chaque push (badge à venir).

---

##  Structure du projet
ensoi/

├── backend/

│   ├── app/

│   │   ├── main.py              # Point d'entrée FastAPI + middleware CORS + rate limiter

│   │   ├── config.py            # Settings Pydantic depuis .env

│   │   ├── database.py          # Connexion PostgreSQL

│   │   ├── rate_limiter.py      # Instance Limiter partagée (slowapi)

│   │   ├── models/              # SQLModel : user, profil, share_token

│   │   ├── schemas/             # Pydantic : auth, profil

│   │   ├── routers/             # Endpoints : auth, users, profils

│   │   └── services/            # Logique métier : numerologie, human_design, profil_cognitif, auth, groq

│   ├── alembic/                 # Migrations BDD versionnées

│   ├── tests/                   # 184 tests pytest

│   └── requirements.txt

├── frontend/

│   ├── src/

│   │   ├── api/                 # Client axios avec JWT en mémoire + refresh auto

│   │   ├── components/          # ErrorBoundary, etc.

│   │   ├── hooks/               # useAuth

│   │   └── pages/               # routes React Router

│   └── tailwind.config.js

└── .github/workflows/           # CI/CD

---

##  Contribution

Git Flow simplifié : `main` ← `develop` ← `feature/*` / `fix/*` / `docs/*`. Convention de commits : `type(scope): description` (feat, fix, test, docs, refactor, chore, security).

---

##  Licence

Projet académique - Stage 2026.
