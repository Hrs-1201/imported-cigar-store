import type { Metadata } from "next";

import { CategoryView } from "@/components/catalog/CategoryView";
import type { CatalogQuery } from "@/lib/catalog";

export const metadata: Metadata = { title: "Lighters" };

export default function LightersPage({ searchParams }: { searchParams: Promise<CatalogQuery> }) {
  return <CategoryView slug="lighters" name="Lighters" searchParams={searchParams} />;
}
