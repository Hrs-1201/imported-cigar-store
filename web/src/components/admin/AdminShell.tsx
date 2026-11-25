"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { useAuth } from "@/components/auth/AuthProvider";
import { ApiRequestError, apiFetch, logoutRequest } from "@/lib/api-client";
import { brand } from "@/lib/brand";
import type { UserPublic } from "@/types/api";

type GateState = { kind: "loading" } | { kind: "admin" } | { kind: "refused" };

export function AdminShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { ready } = useAuth();
  const [state, setState] = useState<GateState>({ kind: "loading" });

  useEffect(() => {
    if (!ready) return;
    let cancelled = false;
    (async () => {
      try {
        const me = await apiFetch<UserPublic>("/auth/me");
        if (cancelled) return;
        setState(me.role === "admin" ? { kind: "admin" } : { kind: "refused" });
      } catch (error) {
        if (cancelled) return;
        if (error instanceof ApiRequestError && error.status === 401) return;
        setState({ kind: "refused" });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [ready]);

  async function onLogout() {
    await logoutRequest();
    router.push("/");
  }

  if (state.kind === "loading") {
    return (
      <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6">
        <p className="text-muted">Checking access…</p>
      </main>
    );
  }

  if (state.kind === "refused") {
    return (
      <main className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6">
        <p className="font-script text-5xl text-gold">{brand.name}</p>
        <h1 className="mt-2 font-serif text-3xl">Admin</h1>
        <p className="mt-6">You do not have access to the admin console.</p>
        <Link href="/" className="mt-6 text-sm font-medium underline">
          Return to the store
        </Link>
      </main>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-gold/40 px-6 py-4">
        <p className="font-script text-3xl text-gold">{brand.name}</p>
        <button type="button" onClick={onLogout} className="text-sm font-medium underline">
          Log out
        </button>
      </header>
      <main className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="font-serif text-3xl">Admin</h1>
        <div className="mt-6">{children}</div>
      </main>
    </div>
  );
}
