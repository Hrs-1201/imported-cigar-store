"use client";

import Link from "next/link";

import { useAuth } from "@/components/auth/AuthProvider";
import { brand } from "@/lib/brand";

function firstName(fullName: string): string {
  const [name] = fullName.trim().split(/\s+/);
  return name || fullName;
}

export function StoreEntry() {
  const { ready, user } = useAuth();

  return (
    <main className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6">
      <p className="font-script text-5xl text-gold">{brand.name}</p>
      <p className="mt-4 text-lg">The shop catalogue will be added in a later phase.</p>
      <div className="mt-8">
        {!ready ? (
          <p className="text-muted">Loading…</p>
        ) : user ? (
          <p>
            {firstName(user.full_name)}{" "}
            <Link href="/account" className="font-medium underline">
              Account
            </Link>
          </p>
        ) : (
          <Link href="/login" className="inline-flex rounded-full bg-ink px-5 py-2.5 text-sm text-white">
            Login
          </Link>
        )}
      </div>
    </main>
  );
}
