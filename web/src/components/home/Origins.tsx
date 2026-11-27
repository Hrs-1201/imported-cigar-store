import Link from "next/link";

const ORIGINS: { country: string; kind: string; note: string; href: string; flag: string }[] = [
  {
    country: "Cuba",
    kind: "Cigar origin",
    note: "The classic island formats.",
    href: "/cigars?origin=Cuba",
    flag: "🇨🇺",
  },
  {
    country: "Dominican Republic",
    kind: "Cigar origin",
    note: "Island formats, listed by the name on the band.",
    href: "/cigars?origin=Dominican%20Republic",
    flag: "🇩🇴",
  },
  {
    country: "Nicaragua",
    kind: "Cigar origin",
    note: "Fuller cigars from Nicaragua.",
    href: "/cigars?origin=Nicaragua",
    flag: "🇳🇮",
  },
  {
    country: "Honduras",
    kind: "Cigar origin",
    note: "Formats grown and rolled in Honduras.",
    href: "/cigars?origin=Honduras",
    flag: "🇭🇳",
  },
  {
    country: "Denmark",
    kind: "Cigarette origin",
    note: "Packs from Denmark, not a cigar valley.",
    href: "/cigarettes?origin=Denmark",
    flag: "🇩🇰",
  },
  {
    country: "Belgium",
    kind: "Cigarette origin",
    note: "Packs from Belgium, not a cigar valley.",
    href: "/cigarettes?origin=Belgium",
    flag: "🇧🇪",
  },
];

export function Origins() {
  return (
    <section id="home-origins" aria-labelledby="home-origins-title" className="min-w-0">
      <header className="mx-auto max-w-lg text-center">
        <p className="text-[11px] tracking-[0.18em] text-gold uppercase">Origins</p>
        <h2 id="home-origins-title" className="mt-4 text-balance font-serif text-3xl sm:text-5xl">
          From the places they were made.
        </h2>
        <p className="mt-4 text-sm leading-6 text-muted sm:text-base">Four cigar countries, plus two cigarette origins.</p>
      </header>
      <ul className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {ORIGINS.map((origin) => (
          <li key={origin.country} className="flex min-w-0 flex-col rounded-[1.75rem] border border-gold bg-white px-5 py-6">
            <span className="text-4xl" aria-hidden>
              {origin.flag}
            </span>
            <h3 className="mt-4 font-serif text-2xl">{origin.country}</h3>
            <p className="mt-1 text-[11px] tracking-[0.14em] text-gold uppercase">{origin.kind}</p>
            <p className="mt-3 text-sm leading-6 text-muted">{origin.note}</p>
            <Link
              href={origin.href}
              className="mt-5 inline-flex w-fit rounded-full border border-ink px-4 py-2 text-sm"
            >
              Explore {origin.country}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
