import type { Metadata } from "next";

import { CategoryView } from "@/components/catalog/CategoryView";
import type { CatalogQuery } from "@/lib/catalog";

export const metadata: Metadata = { title: "Cigarettes" };

export default function CigarettesPage({ searchParams }: { searchParams: Promise<CatalogQuery> }) {
  return <CategoryView slug="cigarettes" name="Cigarettes" searchParams={searchParams} />;
}
