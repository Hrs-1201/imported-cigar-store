"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { getAccessToken, getCurrentUser, subscribe } from "@/lib/auth";
import { refreshSession } from "@/lib/api-client";
import type { UserPublic } from "@/types/api";

type AuthContextValue = {
  user: UserPublic | null;
  ready: boolean;
};

const AuthContext = createContext<AuthContextValue>({ user: null, ready: false });

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserPublic | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const unsubscribe = subscribe(() => setUser(getCurrentUser()));
    let cancelled = false;
    (async () => {
      if (!getAccessToken()) {
        await refreshSession();
      }
      if (!cancelled) {
        setUser(getCurrentUser());
        setReady(true);
      }
    })();
    return () => {
      cancelled = true;
      unsubscribe();
    };
  }, []);

  return <AuthContext.Provider value={{ user, ready }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  return useContext(AuthContext);
}
