import type { Metadata } from "next";

import { CategoryView } from "@/components/catalog/CategoryView";
import type { CatalogQuery } from "@/lib/catalog";

export const metadata: Metadata = { title: "Accessories" };

export default function AccessoriesPage({ searchParams }: { searchParams: Promise<CatalogQuery> }) {
  return <CategoryView slug="accessories" name="Accessories" searchParams={searchParams} />;
}
