import Link from "next/link";

import { ProductCarousel } from "@/components/home/ProductCarousel";
import type { ProductCardList } from "@/types/api";

type ArrivalsResult = { ok: true; data: ProductCardList } | { ok: false; status: number };

export function NewArrivals({ result }: { result: ArrivalsResult }) {
  const items = result.ok ? result.data.items : [];

  return (
    <section id="home-arrivals" aria-labelledby="home-arrivals-title" className="min-w-0">
      <header className="mx-auto max-w-lg text-center">
        <p className="text-[11px] tracking-[0.18em] text-gold uppercase">Just arrived</p>
        <h2 id="home-arrivals-title" className="mt-4 text-balance font-serif text-3xl sm:text-5xl">
          New on the shelf.
        </h2>
        {!result.ok ? (
          <p className="mt-4 text-sm leading-6 sm:text-base">The catalogue is unavailable right now.</p>
        ) : items.length === 0 ? (
          <p className="mt-4 text-sm leading-6 sm:text-base">Nothing is marked as new yet.</p>
        ) : (
          <p className="mt-4 text-sm leading-6 text-muted sm:text-base">
            The latest published products marked as new arrivals.
          </p>
        )}
      </header>
      {items.length > 0 ? (
        <div className="mt-10">
          <ProductCarousel products={items} label="Next arrival" />
        </div>
      ) : null}
      {result.ok ? (
        <div className="mt-8 text-center">
          <Link href="/search?new=1" className="inline-flex rounded-full border border-ink px-5 py-2.5 text-sm">
            View all new arrivals
          </Link>
        </div>
      ) : null}
    </section>
  );
}
