import type { Metadata } from "next";

import { CategoryView } from "@/components/catalog/CategoryView";
import type { CatalogQuery } from "@/lib/catalog";

export const metadata: Metadata = { title: "Cigars" };

export default function CigarsPage({ searchParams }: { searchParams: Promise<CatalogQuery> }) {
  return <CategoryView slug="cigars" name="Cigars" searchParams={searchParams} />;
}
