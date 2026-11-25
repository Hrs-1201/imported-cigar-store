import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ProductDetailView } from "@/components/catalog/ProductDetailView";
import { loadProduct } from "@/lib/catalog";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const result = await loadProduct(slug);
  if (!result.ok) return { title: "Product" };
  return { title: result.data.name };
}

export default async function ProductPage({ params }: Props) {
  const { slug } = await params;
  const result = await loadProduct(slug);
  if (!result.ok) {
    if (result.status === 404) notFound();
    return (
      <main className="mx-auto w-full max-w-[1160px] px-4 py-12">
        <h1 className="font-serif text-4xl">Product</h1>
        <p className="mt-4">The catalogue is unavailable right now.</p>
      </main>
    );
  }
  return <ProductDetailView product={result.data} />;
}
