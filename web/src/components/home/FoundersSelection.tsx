import { ProductCarousel } from "@/components/home/ProductCarousel";
import type { ProductCardList } from "@/types/api";

type FeaturedResult = { ok: true; data: ProductCardList } | { ok: false; status: number };

export function FoundersSelection({ result }: { result: FeaturedResult }) {
  const items = result.ok ? result.data.items : [];
  const empty = result.ok && items.length === 0;

  return (
    <section id="home-founder" aria-labelledby="home-founder-title" className="min-w-0">
      <header className="mx-auto max-w-lg text-center">
        <p className="text-[11px] tracking-[0.18em] text-gold uppercase">Founder&apos;s selection</p>
        <h2 id="home-founder-title" className="mt-4 text-balance font-serif text-[1.65rem] leading-tight uppercase sm:text-4xl lg:text-5xl">
          Not every cigar.
          <span className="block">Only the ones we stock.</span>
        </h2>
        <p className="mt-4 text-sm leading-6 text-muted sm:text-base">
          A short list marked by the shop. Rank, price, and format
          <br className="hidden sm:block" /> come from the product record — not from a slogan.
        </p>
      </header>
      {!result.ok ? (
        <p className="mt-10 text-center">The catalogue is unavailable right now.</p>
      ) : empty ? (
        <p className="mt-10 text-center text-lg">
          The founder’s list is empty. It will show here once an admin marks products.
        </p>
      ) : (
        <div className="mt-10">
          <ProductCarousel products={items} label="Next founder pick" />
        </div>
      )}
    </section>
  );
}
