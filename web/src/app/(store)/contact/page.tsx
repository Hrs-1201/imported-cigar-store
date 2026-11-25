import type { Metadata } from "next";

import { ContactForm } from "@/components/contact/ContactForm";

export const metadata: Metadata = { title: "Contact Us" };

export default function ContactPage() {
  return (
    <main className="mx-auto w-full max-w-xl px-4 py-14">
      <h1 className="font-serif text-4xl">Contact Us</h1>
      <p className="mt-4 text-muted">Write to the shop about stock, shipping, or something you cannot find on the shelf.</p>
      <ContactForm />
      <section id="shipping" className="mt-12 border-t border-gold/30 pt-8">
        <h2 className="font-serif text-2xl">Shipping</h2>
        <p className="mt-3 text-muted">
          We pack discreetly and ship only where the sale is lawful. The shop confirms delivery before anything leaves.
        </p>
      </section>
    </main>
  );
}
