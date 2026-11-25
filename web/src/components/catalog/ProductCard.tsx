import Link from "next/link";

import { ProductPhoto } from "@/components/catalog/ProductPhoto";
import { ProductSpecs } from "@/components/catalog/ProductSpecs";
import { PurchaseControls } from "@/components/catalog/PurchaseControls";
import { formatInr, phrase, scoreLabel } from "@/lib/format";
import type { ProductCard as ProductCardData } from "@/types/api";

export function ProductCard({ product }: { product: ProductCardData }) {
  const href = `/products/${product.slug}`;
  return (
    <article className="flex h-full min-w-0 flex-col overflow-hidden rounded-2xl border border-gold/30 bg-white shadow-sm">
      <div className="relative">
        <Link href={href} className="block">
          <ProductPhoto
            src={product.primary_image?.public_path ?? null}
            alt={product.primary_image?.alt_text ?? product.name}
            brand={product.brand}
            className="aspect-[3/4] w-full"
          />
        </Link>
        <div className="pointer-events-none absolute top-3 left-3 flex max-w-[70%] flex-wrap gap-2">
          {product.category_slug === "cigars" && product.founder_rank != null ? (
            <span className="flex h-14 w-14 flex-col items-center justify-center rounded-full bg-white text-center shadow-sm">
              <span className="font-serif text-sm leading-none">#{product.founder_rank}</span>
              <span className="mt-0.5 px-1 text-[7px] leading-tight tracking-wide uppercase">Founder&apos;s pick</span>
            </span>
          ) : null}
          {product.ratings.map((rating) => (
            <span
              key={rating.source_name}
              title={rating.source_name}
              className="flex h-14 w-14 flex-col items-center justify-center rounded-full bg-white px-1 text-center shadow-sm"
            >
              <span className="font-serif text-sm leading-none">{scoreLabel(rating.score)}</span>
              <span className="mt-0.5 line-clamp-2 text-[7px] leading-tight tracking-wide uppercase">
                {rating.source_name}
              </span>
            </span>
          ))}
        </div>
        {product.low_stock ? (
          <span className="absolute top-3 right-3 rounded-full bg-ink px-2.5 py-1 text-[10px] text-white">
            Only {product.stock_qty} left
          </span>
        ) : null}
      </div>
      <div className="flex flex-1 flex-col px-4 pt-4 pb-5">
        <p className="text-[11px] tracking-[0.16em] text-gold uppercase">{product.brand}</p>
        {product.category_slug === "cigars" && product.subtype ? (
          <p className="mt-1 text-[11px] tracking-[0.14em] text-muted uppercase">{phrase(product.subtype)}</p>
        ) : null}
        <h2 className="mt-2 font-serif text-xl break-words">
          <Link href={href}>{product.name}</Link>
        </h2>
        <p className="mt-2 text-lg tabular-nums">{formatInr(product.price_inr)}</p>
        <p className="text-xs text-muted">Price is for one unit.</p>
        {product.category_slug === "cigars" && product.origin_label ? (
          <p className="mt-1 text-sm text-muted">{product.origin_label}</p>
        ) : null}
        {product.extra_ratings_count > 0 ? (
          <Link href={href} className="mt-2 text-xs text-muted underline">
            +{product.extra_ratings_count} more ratings
          </Link>
        ) : null}
        <ProductSpecs product={product} />
        <div className="mt-auto">
          <PurchaseControls stockQty={product.stock_qty} inStock={product.in_stock} />
        </div>
      </div>
    </article>
  );
}
