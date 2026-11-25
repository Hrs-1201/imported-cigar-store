import type { ReactNode } from "react";

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
    <main className="mx-auto flex w-full max-w-md flex-col px-6 py-16">
      <h1 className="font-serif text-3xl">{title}</h1>
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
