import type { Metadata } from "next";

export const metadata: Metadata = { title: "Terms" };

export default function TermsPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-16">
      <h1 className="font-serif text-4xl">Terms</h1>
      <p className="mt-4 text-muted">
        The shop is not taking orders yet. The price on a product card is the unit price recorded for that product.
        These terms will be completed before checkout opens.
      </p>
    </main>
  );
}
