import type { BrandList } from "@/types/api";

type BrandsResult = { ok: true; data: BrandList } | { ok: false; status: number };

export function BrandsRow({ result }: { result: BrandsResult }) {
  if (result.ok && result.data.items.length === 0) return null;

  return (
    <section id="home-brands" aria-labelledby="home-brands-title" className="min-w-0">
      <h2 id="home-brands-title" className="text-center text-[11px] tracking-[0.18em] text-gold uppercase">
        Brands we carry
      </h2>
      <p className="mt-3 text-center text-muted">Names on the shelf right now.</p>
      {!result.ok ? (
        <p className="mt-8 text-center">The catalogue is unavailable right now.</p>
      ) : (
        <div className="mt-8 min-w-0 overflow-x-auto overscroll-x-contain">
          <ul className="mx-auto flex w-max min-w-full items-center justify-center py-1">
            {result.data.items.map((name, index) => (
              <li
                key={name}
                className={`shrink-0 px-4 font-serif text-lg sm:px-5 sm:text-xl ${
                  index > 0 ? "border-l border-ink/15" : ""
                }`}
              >
                {name}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
