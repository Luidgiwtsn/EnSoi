import { createContext, useState, useEffect, useCallback, useRef } from 'react';
import {
  authApi,
  usersApi,
  profilsApi,
  tokenStore,
  pendingClaimStore,
} from '../api/client';

/**
 * Context d'authentification - source de verite globale pour l'utilisateur connecte.
 *
 * Ne pas consommer directement ce Context : passer par le hook useAuth.
 *
 * Bootstrap au montage :
 * - Si un refresh_token est en localStorage (cas du F5 ou nouvel onglet),
 *   on l'echange contre un nouveau couple via /auth/refresh, puis on hydrate
 *   user via /users/me.
 * - Sinon, on reste anonyme.
 *
 * Le bootstrap est protege contre le double-mount de React.StrictMode via un
 * useRef. Le refresh_token est one-shot cote backend (rotation a chaque
 * /auth/refresh), donc l'appeler deux fois avec le meme token entraine un 401
 * sur le second appel et deconnecte l'user a tort. Le ref garantit qu'un seul
 * bootstrap est lance par cycle de vie de l'AuthProvider.
 *
 * Ecoute aussi l'event 'auth:expired' emis par client.js quand le refresh
 * echoue en cours de session (deconnexion silencieuse cote client).
 *
 * Apres login/register reussi, tente automatiquement le claim d'un profil
 * anonyme en attente dans pendingClaimStore (scenario 3).
 */
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const bootstrapStartedRef = useRef(false);

  // --- Bootstrap au montage ---
  useEffect(() => {
    if (bootstrapStartedRef.current) return;
    bootstrapStartedRef.current = true;

    (async () => {
      if (!tokenStore.hasRefresh()) {
        setLoading(false);
        return;
      }
      try {
        const tokensRes = await authApi.refresh(tokenStore.refresh);
        tokenStore.set(tokensRes.data);

        const meRes = await usersApi.me();
        setUser(meRes.data);
      } catch (err) {
        tokenStore.clear();
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // --- Reaction a l'event auth:expired ---
  useEffect(() => {
    const handleExpired = () => {
      setUser(null);
      tokenStore.clear();
    };
    window.addEventListener('auth:expired', handleExpired);
    return () => window.removeEventListener('auth:expired', handleExpired);
  }, []);

  // --- Helper interne : tente le claim si un profil anonyme est en attente ---
  const claimPendingProfilIfAny = useCallback(async () => {
    const pending = pendingClaimStore.get();
    if (!pending) return null;
    try {
      await profilsApi.claim(pending.profilId, pending.claimToken);
      pendingClaimStore.clear();
      return pending.profilId;
    } catch (err) {
      pendingClaimStore.clear();
      return null;
    }
  }, []);

  // --- Login ---
  const login = useCallback(
    async (email, password) => {
      const tokensRes = await authApi.login({ email, password });
      tokenStore.set(tokensRes.data);

      const meRes = await usersApi.me();
      setUser(meRes.data);

      const claimedProfilId = await claimPendingProfilIfAny();
      return { user: meRes.data, claimedProfilId };
    },
    [claimPendingProfilIfAny]
  );

  // --- Register ---
  const register = useCallback(
    async (data) => {
      const tokensRes = await authApi.register(data);
      tokenStore.set(tokensRes.data);

      const meRes = await usersApi.me();
      setUser(meRes.data);

      const claimedProfilId = await claimPendingProfilIfAny();
      return { user: meRes.data, claimedProfilId };
    },
    [claimPendingProfilIfAny]
  );

  // --- Logout ---
  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch (err) {
      // silencieux : on deconnecte cote client quoi qu'il arrive
    }
    tokenStore.clear();
    setUser(null);
  }, []);

  const value = {
    user,
    isAuthenticated: user !== null,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
