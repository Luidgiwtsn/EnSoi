import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Stockage des tokens EN MÉMOIRE uniquement (jamais localStorage)
let accessToken = null;
let refreshToken = null;
let refreshPromise = null;

export const tokenStore = {
  get access() { return accessToken; },
  get refresh() { return refreshToken; },
  set(tokens) {
    accessToken = tokens?.access_token ?? null;
    refreshToken = tokens?.refresh_token ?? null;
  },
  clear() {
    accessToken = null;
    refreshToken = null;
  },
  has() { return Boolean(accessToken); },
};


// Stockage du claim_token (UUID one-shot pour rattacher un profil anonyme)
// SessionStorage : persiste tant que l'onglet est ouvert, disparait a la fermeture.
// Volontairement different du tokenStore : ici l'utilisateur n'est PAS authentifie,
// le claim_token n'est pas un secret de session, juste un identifiant temporaire
// permettant de retrouver le profil genere en mode anonyme apres inscription.
const CLAIM_KEY = 'ensoi_pending_claim';

export const pendingClaimStore = {
  /**
   * Stocke un claim apres generation anonyme.
   * @param {{ profilId: number, claimToken: string }} payload
   */
  set({ profilId, claimToken }) {
    try {
      sessionStorage.setItem(CLAIM_KEY, JSON.stringify({
        profilId,
        claimToken,
        createdAt: Date.now(),
      }));
    } catch (e) {
      // sessionStorage indisponible (mode prive, quota) : silencieux
      console.warn('pendingClaimStore.set a echoue:', e);
    }
  },

  /**
   * Recupere le claim en attente ou null s'il n'y en a pas.
   * @returns {{ profilId: number, claimToken: string, createdAt: number } | null}
   */
  get() {
    try {
      const raw = sessionStorage.getItem(CLAIM_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },

  /** Efface le claim en attente (apres usage ou abandon). */
  clear() {
    try {
      sessionStorage.removeItem(CLAIM_KEY);
    } catch (e) {
      // silencieux
    }
  },

  /** True s'il y a un claim en attente. */
  has() {
    return Boolean(this.get());
  },
};


const client = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status !== 401 ||
      originalRequest._retry ||
      !refreshToken ||
      originalRequest.url?.includes('/auth/refresh')
    ) {
      return Promise.reject(error);
    }
    originalRequest._retry = true;
    try {
      if (!refreshPromise) {
        refreshPromise = axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
      }
      const { data } = await refreshPromise;
      refreshPromise = null;
      tokenStore.set(data);
      originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      return client(originalRequest);
    } catch (refreshError) {
      refreshPromise = null;
      tokenStore.clear();
      window.dispatchEvent(new CustomEvent('auth:expired'));
      return Promise.reject(refreshError);
    }
  }
);

export const authApi = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  logout: () => client.post('/auth/logout'),
  refresh: (refresh_token) => client.post('/auth/refresh', { refresh_token }),
  changePassword: (data) => client.post('/auth/change-password', data),
};

export const usersApi = {
  me: () => client.get('/users/me'),
  update: (data) => client.patch('/users/me', data),
  updateEmail: (data) => client.patch('/users/me/email', data),
  delete: (password) => client.delete('/users/me', { data: { password } }),
};

export const profilsApi = {
  generate: (data) => client.post('/api/generate', data),
  list: () => client.get('/api/profils'),
  get: (id) => client.get(`/api/profils/${id}`),
  delete: (id) => client.delete(`/api/profils/${id}`),
  share: (id) => client.post(`/api/profils/${id}/share`),
  claim: (id, claim_token) => client.post(`/api/profils/${id}/claim`, { claim_token }),
  public: (token) => client.get(`/public/${token}`),
  health: () => client.get('/api/health'),
  cognitif: () => client.get('/api/cognitif/questions'),
  countries: () => client.get('/api/countries'),
  timezones: () => client.get('/api/timezones'),
};

export default client;
