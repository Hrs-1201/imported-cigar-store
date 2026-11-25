import type { ReactNode } from "react";

import { brand } from "@/lib/brand";

export const inputClassName =
  "w-full rounded-md border border-gold/40 bg-white px-3 py-2 text-ink outline-none focus:border-ink";

export const buttonClassName =
  "inline-flex w-full items-center justify-center rounded-full bg-ink px-5 py-2.5 text-sm text-white disabled:opacity-60";

export function AuthScreen({
  title,
  children,
  alternate,
}: {
  title: string;
  children: ReactNode;
  alternate?: ReactNode;
}) {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-16">
      <p className="font-script text-5xl text-gold">{brand.name}</p>
      <h1 className="mt-2 font-serif text-3xl">{title}</h1>
      <div className="mt-8">{children}</div>
      {alternate ? <p className="mt-6 text-sm text-muted">{alternate}</p> : null}
    </main>
  );
}

export function Field({
  id,
  label,
  error,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm">
        {label}
      </label>
      {children}
      {error ? <p className="mt-1 text-sm text-red-800">{error}</p> : null}
    </div>
  );
}
