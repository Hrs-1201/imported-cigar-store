import type { Metadata } from "next";

import { SearchResults } from "@/components/catalog/SearchResults";
import type { CatalogQuery } from "@/lib/catalog";

export const metadata: Metadata = { title: "Search" };

export default function SearchPage({ searchParams }: { searchParams: Promise<CatalogQuery> }) {
  return <SearchResults searchParams={searchParams} />;
}
