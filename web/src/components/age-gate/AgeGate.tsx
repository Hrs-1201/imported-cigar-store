"use client";

import { useEffect, useState, type ReactNode } from "react";

import { brand } from "@/lib/brand";

const AGE_GATE_KEY = "age_gate";
const AGE_GATE_VALUE = "21";

export function AgeGate({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    const confirmed = window.sessionStorage.getItem(AGE_GATE_KEY) === AGE_GATE_VALUE;
    // sessionStorage is unavailable during SSR. Read it after mount so the first paint matches the server.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setAllowed(confirmed);
    setReady(true);
  }, []);

  if (!ready) {
    return <div className="min-h-screen bg-paper" />;
  }

  if (!allowed) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper px-6">
        <section
          role="dialog"
          aria-modal="true"
          aria-labelledby="age-gate-title"
          className="w-full max-w-md border border-gold/50 bg-white px-8 py-10 text-center"
        >
          <p className="font-script text-5xl text-gold">{brand.name}</p>
          <p className="mt-6 text-ink">This shop sells tobacco products.</p>
          <h1 id="age-gate-title" className="mt-2 font-serif text-2xl text-ink">
            You must be 21 or older to enter.
          </h1>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <button
              type="button"
              className="rounded-full bg-ink px-5 py-2.5 text-sm text-white"
              onClick={() => {
                window.sessionStorage.setItem(AGE_GATE_KEY, AGE_GATE_VALUE);
                setAllowed(true);
              }}
            >
              I am 21 or older
            </button>
            <button
              type="button"
              className="rounded-full border border-ink px-5 py-2.5 text-sm text-ink"
              onClick={() => {
                window.location.href = "https://www.google.com";
              }}
            >
              Leave
            </button>
          </div>
        </section>
      </div>
    );
  }

  return children;
}
