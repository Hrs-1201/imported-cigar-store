import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Site map" };

const ROUTES = [
  ["/", "Home"],
  ["/cigars", "Cigars"],
  ["/cigarettes", "Cigarettes"],
  ["/lighters", "Lighters"],
  ["/accessories", "Accessories"],
  ["/search", "Search"],
  ["/search?new=1", "New arrivals"],
  ["/contact", "Contact Us"],
  ["/cart", "Cart"],
  ["/login", "Login"],
  ["/register", "Register"],
  ["/account", "Account"],
  ["/legal/privacy", "Privacy"],
  ["/legal/terms", "Terms"],
  ["/legal/age", "Age & tobacco"],
];

export default function SitemapPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-16">
      <h1 className="font-serif text-4xl">Site map</h1>
      <ul className="mt-8 space-y-2">
        {ROUTES.map(([href, label]) => (
          <li key={href}>
            <Link href={href} className="underline">
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
