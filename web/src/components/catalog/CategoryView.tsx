import Link from "next/link";

import { Pager } from "@/components/catalog/Pager";
import { ProductGrid } from "@/components/catalog/ProductGrid";
import { type CatalogQuery, loadCategoryProducts, pageNumber, textParam } from "@/lib/catalog";

export async function CategoryView({
  slug,
  name,
  searchParams,
}: {
  slug: string;
  name: string;
  searchParams: Promise<CatalogQuery>;
}) {
  const query = await searchParams;
  const origin = textParam(query.origin);
  const q = textParam(query.q);
  const page = pageNumber(query.page);
  const result = await loadCategoryProducts(slug, { origin, q, page });
  const filtered = Boolean(origin || q);

  return (
    <main className="mx-auto w-full max-w-[1160px] px-4 py-12">
      <h1 className="font-serif text-4xl sm:text-5xl">{name}</h1>
      {origin ? (
        <p className="mt-3 text-sm text-muted">
          Origin: {origin}.{" "}
          <Link href={`/${slug}`} className="underline">
            Show all
          </Link>
        </p>
      ) : null}
      {q ? <p className="mt-2 text-sm text-muted">Matching “{q}”.</p> : null}
      {!result.ok ? (
        <p className="mt-10">The catalogue is unavailable right now.</p>
      ) : result.data.items.length === 0 ? (
        <p className="mt-10 text-lg">
          {filtered ? `Nothing is listed in ${name} for this filter.` : `Nothing is listed in ${name} yet.`}
        </p>
      ) : (
        <>
          <div className="mt-10">
            <ProductGrid products={result.data.items} />
          </div>
          <Pager
            pathname={`/${slug}`}
            params={{ origin: origin || undefined, q: q || undefined }}
            page={result.data.page}
            pageSize={result.data.page_size}
            total={result.data.total}
          />
        </>
      )}
    </main>
  );
}
