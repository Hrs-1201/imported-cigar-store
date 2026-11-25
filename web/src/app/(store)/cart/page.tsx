import type { Metadata } from "next";

export const metadata: Metadata = { title: "Cart" };

export default function CartPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-16">
      <h1 className="font-serif text-4xl">Cart</h1>
      <p className="mt-4 text-lg">Cart arrives in a later phase.</p>
    </main>
  );
}
