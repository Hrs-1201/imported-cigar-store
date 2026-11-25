import Link from "next/link";

import { brand } from "@/lib/brand";

const WARNING = `STATUTORY WARNING
TOBACCO SMOKING IS INJURIOUS TO HEALTH. SALE TO PERSONS UNDER 18
IS PROHIBITED UNDER THE COTPA ACT 2003.

OUR HOUSE POLICY
ASH & CEDAR SELLS ONLY TO ADULTS AGED 21 AND ABOVE.`;

const COLUMNS: { title: string; links: { href: string; label: string }[] }[] = [
  {
    title: "Cigars & more",
    links: [
      { href: "/cigars", label: "Cigars" },
      { href: "/cigarettes", label: "Cigarettes" },
      { href: "/search?new=1", label: "All new arrivals" },
    ],
  },
  {
    title: "Accessories",
    links: [
      { href: "/lighters", label: "Lighters" },
      { href: "/accessories", label: "Cutters" },
      { href: "/accessories", label: "Ashtrays" },
    ],
  },
  {
    title: "Help",
    links: [
      { href: "/contact", label: "Contact Us" },
      { href: "/contact#shipping", label: "Shipping note" },
    ],
  },
  {
    title: "Account",
    links: [
      { href: "/login", label: "Login" },
      { href: "/register", label: "Register" },
      { href: "/account", label: "Account" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/legal/privacy", label: "Privacy" },
      { href: "/legal/terms", label: "Terms" },
      { href: "/legal/age", label: "Age & tobacco" },
    ],
  },
];

export function Footer() {
  const year = new Date().getFullYear();
  const grievance = [brand.grievanceName, brand.grievanceEmail, brand.grievancePhone].filter((value) => value.length > 0);

  return (
    <footer className="mt-16 border-t border-gold/40 bg-paper">
      <div className="mx-auto w-full max-w-[1160px] px-4 py-12">
        <p className="font-script text-5xl text-gold">{brand.name}</p>
        <p className="mt-3 max-w-md text-sm text-muted">{brand.description}</p>
        <div className="mt-10 grid grid-cols-2 gap-8 sm:grid-cols-3 lg:grid-cols-5">
          {COLUMNS.map((column) => (
            <div key={column.title} className="min-w-0">
              <p className="text-[11px] tracking-[0.16em] text-gold uppercase">{column.title}</p>
              <ul className="mt-3 space-y-2 text-sm">
                {column.links.map((link) => (
                  <li key={`${column.title}-${link.label}`}>
                    <Link href={link.href} className="hover:underline">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        {grievance.length > 0 ? (
          <p className="mt-8 text-sm text-muted">{grievance.join(" · ")}</p>
        ) : null}
        <p className="mt-10 text-sm">Buy only if you are 21 or older.</p>
        <div className="mt-4 border border-warning px-4 py-5 text-center text-xs tracking-wide whitespace-pre-line text-warning uppercase">
          {WARNING}
        </div>
        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-muted">© {year} Ash & Cedar. All rights reserved.</p>
          <div className="flex gap-3">
            <Link href="/sitemap" className="rounded-full border border-ink px-4 py-2 text-sm">
              Site map
            </Link>
            <Link href="/legal/terms" className="rounded-full border border-ink px-4 py-2 text-sm">
              Terms
            </Link>
          </div>
        </div>
        {brand.phone ? (
          <a className="mt-6 inline-flex text-sm underline" href={`https://wa.me/${brand.phone}`}>
            WhatsApp
          </a>
        ) : null}
      </div>
    </footer>
  );
}
