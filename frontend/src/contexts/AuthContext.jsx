import { createContext, useState, useEffect, useCallback } from 'react';
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
 * Ne pas consommer directement ce Context : passer par le hook useAuth (hooks/useAuth.js).
 *
 * Comportements importants :
 * - Au montage, tente un bootstrap via /users/me si un token est en memoire.
 *   Note : tokenStore est en RAM, donc apres un F5 l'utilisateur est deconnecte.
 *   Choix de design assume (anti-XSS)
 * - Ecoute l'event 'auth:expired' emis par client.js quand le refresh echoue.
 * - Apres login/register reussi, tente automatiquement un claim si un profil
 *   anonyme est en attente dans le pendingClaimStore (scenario 3).
 */
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // --- Bootstrap au montage ---
  // Si un token est present en memoire (cas rare : navigation interne sans F5),
  // on hydrate user via /users/me. Sinon, on reste anonyme.
  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      if (!tokenStore.has()) {
        if (!cancelled) setLoading(false);
        return;
      }
      try {
        const res = await usersApi.me();
        if (!cancelled) setUser(res.data);
      } catch (err) {
        // 401 ou autre : token invalide, on nettoie
        tokenStore.clear();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  // --- Reaction a l'event auth:expired (emis par client.js quand le refresh echoue) ---
  useEffect(() => {
    const handleExpired = () => {
      setUser(null);
      tokenStore.clear();
    };
    window.addEventListener('auth:expired', handleExpired);
    return () => window.removeEventListener('auth:expired', handleExpired);
  }, []);

  // --- Helper interne : tente le claim si un profil anonyme est en attente ---
  // Retourne l'id du profil rattache, ou null si pas de claim a faire / echec silencieux.
  const claimPendingProfilIfAny = useCallback(async () => {
    const pending = pendingClaimStore.get();
    if (!pending) return null;
    try {
      await profilsApi.claim(pending.profilId, pending.claimToken);
      pendingClaimStore.clear();
      return pending.profilId;
    } catch (err) {
      // Token perime, profil deja claime, profil supprime, etc.
      // On nettoie silencieusement, l'utilisateur reste connecte normalement.
      pendingClaimStore.clear();
      return null;
    }
  }, []);

  // --- Login ---
  // Retourne { user, claimedProfilId } - les pages utilisent claimedProfilId pour rediriger
  // vers le profil rattache plutot que vers le dashboard.
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
  // Meme logique que login : register renvoie deja des tokens, on les stocke,
  // on hydrate user via /users/me (pour avoir l'objet complet), puis claim eventuel.
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
  // Best-effort : on tente l'invalidation backend du refresh token,
  // mais meme si ca echoue (reseau down, token deja invalide), on nettoie cote client.
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
