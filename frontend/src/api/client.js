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
  public: (token) => client.get(`/public/${token}`),
  health: () => client.get('/api/health'),
};

export default client;
