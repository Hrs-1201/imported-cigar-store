"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiRequestError, apiFetch, logoutRequest } from "@/lib/api-client";
import { getAccessToken } from "@/lib/auth";
import { useAuth } from "@/components/auth/AuthProvider";
import type { UserPublic } from "@/types/api";

export function AccountView() {
  const router = useRouter();
  const { ready } = useAuth();
  const [profile, setProfile] = useState<UserPublic | null>(null);

  useEffect(() => {
    if (!ready) return;
    let cancelled = false;
    (async () => {
      if (!getAccessToken()) {
        router.replace("/login?next=/account");
        return;
      }
      try {
        const me = await apiFetch<UserPublic>("/auth/me");
        if (!cancelled) setProfile(me);
      } catch (error) {
        if (cancelled) return;
        if (error instanceof ApiRequestError && error.status === 401) return;
        router.replace("/login?next=/account");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [ready, router]);

  async function onLogout() {
    await logoutRequest();
    router.push("/");
  }

  return (
    <main className="mx-auto w-full max-w-lg px-6 py-16">
      <h1 className="font-serif text-3xl">Account</h1>
      {!profile ? (
        <p className="mt-8 text-muted">Loading…</p>
      ) : (
        <div className="mt-8 space-y-4">
          <p>
            <span className="block text-sm text-muted">Name</span>
            {profile.full_name}
          </p>
          <p>
            <span className="block text-sm text-muted">Email</span>
            {profile.email}
          </p>
          <button type="button" onClick={onLogout} className="text-sm font-medium underline">
            Log out
          </button>
        </div>
      )}
    </main>
  );
}
