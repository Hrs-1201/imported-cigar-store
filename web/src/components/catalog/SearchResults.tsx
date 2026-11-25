import { Pager } from "@/components/catalog/Pager";
import { ProductGrid } from "@/components/catalog/ProductGrid";
import { type CatalogQuery, loadSearch, pageNumber, textParam } from "@/lib/catalog";

export async function SearchResults({ searchParams }: { searchParams: Promise<CatalogQuery> }) {
  const query = await searchParams;
  const q = textParam(query.q);
  const origin = textParam(query.origin);
  const isNew = textParam(query.new) === "1";
  const page = pageNumber(query.page);
  const searched = Boolean(q) || isNew;
  const result = await loadSearch({ q, origin, newFlag: isNew, page });

  let heading = "Search";
  if (isNew && q) heading = `New arrivals matching “${q}”`;
  else if (isNew) heading = "New arrivals";
  else if (q) heading = `Results for “${q}”`;

  let empty = "Search by name or brand.";
  if (isNew && !q) empty = "Nothing is marked as new yet.";
  else if (q) empty = `No products match “${q}”.`;

  return (
    <main className="mx-auto w-full max-w-[1160px] px-4 py-12">
      <h1 className="font-serif text-4xl sm:text-5xl">{heading}</h1>
      <form action="/search" className="mt-6 flex max-w-xl gap-2">
        <label className="sr-only" htmlFor="search-q">
          Search by name or brand
        </label>
        <input
          id="search-q"
          name="q"
          defaultValue={q}
          placeholder="Search by name or brand"
          className="min-w-0 flex-1 rounded-full border border-gold/40 bg-white px-4 py-2 text-sm outline-none focus:border-ink"
        />
        <button type="submit" className="shrink-0 rounded-full bg-ink px-4 text-sm text-white">
          Search
        </button>
      </form>
      {origin ? <p className="mt-3 text-sm text-muted">Origin: {origin}</p> : null}
      {!result.ok ? (
        <p className="mt-10">The catalogue is unavailable right now.</p>
      ) : !searched || result.data.items.length === 0 ? (
        <p className="mt-10 text-lg">{empty}</p>
      ) : (
        <>
          <div className="mt-10">
            <ProductGrid products={result.data.items} />
          </div>
          <Pager
            pathname="/search"
            params={{ q: q || undefined, origin: origin || undefined, new: isNew ? "1" : undefined }}
            page={result.data.page}
            pageSize={result.data.page_size}
            total={result.data.total}
          />
        </>
      )}
    </main>
  );
}
