import type { Metadata } from "next";

export const metadata: Metadata = { title: "Age & tobacco" };

export default function AgePage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-16">
      <h1 className="font-serif text-4xl">Age & tobacco</h1>
      <p className="mt-4">You must be 21 or older to use this shop.</p>
      <p className="mt-4 text-muted">
        Tobacco smoking is injurious to health. Sale to persons under 18 is prohibited under the COTPA Act 2003. Ash
        & Cedar sells only to adults aged 21 and above.
      </p>
    </main>
  );
}
