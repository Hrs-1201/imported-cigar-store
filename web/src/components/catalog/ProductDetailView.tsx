import Link from "next/link";

import { ProductPhoto } from "@/components/catalog/ProductPhoto";
import { ProductSpecs } from "@/components/catalog/ProductSpecs";
import { PurchaseControls } from "@/components/catalog/PurchaseControls";
import { formatInr, phrase } from "@/lib/format";
import type { ProductDetail } from "@/types/api";

export function ProductDetailView({ product }: { product: ProductDetail }) {
  const images = product.images.length > 0 ? product.images : product.primary_image ? [product.primary_image] : [];
  return (
    <main className="mx-auto w-full max-w-[1160px] px-4 py-12">
      <p className="text-sm text-muted">
        <Link href={`/${product.category_slug}`} className="underline">
          {product.category_name}
        </Link>
      </p>
      <div className="mt-6 grid gap-10 lg:grid-cols-2">
        <div className="min-w-0 space-y-3">
          {images.length === 0 ? (
            <ProductPhoto src={null} alt={product.name} brand={product.brand} className="aspect-[3/4] w-full rounded-2xl" />
          ) : (
            images.map((image) => (
              <ProductPhoto
                key={image.id}
                src={image.public_path}
                alt={image.alt_text}
                brand={product.brand}
                className="aspect-[3/4] w-full rounded-2xl"
              />
            ))
          )}
        </div>
        <div className="min-w-0">
          <p className="text-[11px] tracking-[0.16em] text-gold uppercase">{product.brand}</p>
          <h1 className="mt-2 font-serif text-4xl break-words">{product.name}</h1>
          <p className="mt-4 text-2xl tabular-nums">{formatInr(product.price_inr)}</p>
          <p className="text-sm text-muted">Price is for one unit.</p>
          {product.origin_label ? <p className="mt-2 text-muted">{product.origin_label}</p> : null}
          {product.short_description ? <p className="mt-4">{product.short_description}</p> : null}
          {product.description ? <p className="mt-3 text-muted">{product.description}</p> : null}
          {product.category_slug === "cigars" && product.founder_rank != null ? (
            <p className="mt-4 text-sm tracking-[0.14em] uppercase">Founder&apos;s pick #{product.founder_rank}</p>
          ) : null}
          {product.subtype ? <p className="mt-2 text-sm text-muted">{phrase(product.subtype)}</p> : null}
          <ProductSpecs product={product} />
          {product.ratings.length > 0 ? (
            <ul className="mt-4 space-y-1 text-sm">
              {product.ratings.map((rating) => (
                <li key={`${rating.source_name}-${rating.score}`}>
                  {rating.source_name}: {rating.score}
                </li>
              ))}
            </ul>
          ) : null}
          {!product.in_stock ? <p className="mt-4 text-sm">Out of stock</p> : null}
          {product.low_stock ? <p className="mt-4 text-sm">Only {product.stock_qty} left</p> : null}
          <PurchaseControls stockQty={product.stock_qty} inStock={product.in_stock} />
          <p className="mt-6 text-xs text-muted">SKU {product.sku}</p>
        </div>
      </div>
    </main>
  );
}
