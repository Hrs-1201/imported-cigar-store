import type { Metadata } from "next";

export const metadata: Metadata = { title: "Privacy" };

export default function PrivacyPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-16">
      <h1 className="font-serif text-4xl">Privacy</h1>
      <p className="mt-4 text-muted">
        An account stores the name, email, and phone you submit, plus the date of birth used for the age check. The 21+
        acknowledgement stays in this browser tab and is not sent to the server. This note will be expanded before the
        shop takes orders.
      </p>
    </main>
  );
}
