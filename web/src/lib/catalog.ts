import { cache } from "react";

import type { BrandList, ProductCardList, ProductDetail, ProductPage } from "@/types/api";

export type CatalogQuery = {
  origin?: string;
  q?: string;
  page?: string;
  new?: string;
};

function apiOrigin(): string {
  return (process.env.API_ORIGIN ?? "http://127.0.0.1:8000").replace(/\/$/, "");
}

export async function catalogGet<T>(path: string): Promise<{ ok: true; data: T } | { ok: false; status: number }> {
  try {
    const response = await fetch(`${apiOrigin()}/api/v1${path}`, { cache: "no-store" });
    if (!response.ok) return { ok: false, status: response.status };
    return { ok: true, data: (await response.json()) as T };
  } catch {
    return { ok: false, status: 0 };
  }
}

export function textParam(value: unknown): string {
  const raw = Array.isArray(value) ? value[0] : value;
  return typeof raw === "string" ? raw.trim() : "";
}

export function pageNumber(value: unknown): number {
  const parsed = Number(textParam(value));
  if (!Number.isInteger(parsed) || parsed < 1) return 1;
  return parsed;
}

export function searchString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === "") continue;
    search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

export const loadProduct = cache(async (slug: string) => {
  return catalogGet<ProductDetail>(`/products/${encodeURIComponent(slug)}`);
});

export async function loadCategoryProducts(
  slug: string,
  query: { origin?: string; q?: string; page: number },
): Promise<{ ok: true; data: ProductPage } | { ok: false; status: number }> {
  const path = `/categories/${encodeURIComponent(slug)}/products${searchString({
    origin: query.origin?.trim() || undefined,
    q: query.q?.trim() || undefined,
    page: query.page > 1 ? query.page : undefined,
  })}`;
  return catalogGet<ProductPage>(path);
}

export function loadBrands() {
  return catalogGet<BrandList>("/brands");
}

export function loadFeatured() {
  return catalogGet<ProductCardList>("/products/featured");
}

export function loadNewArrivals() {
  return catalogGet<ProductCardList>("/products/new-arrivals");
}

export async function loadSearch(query: {
  q?: string;
  origin?: string;
  newFlag: boolean;
  page: number;
}): Promise<{ ok: true; data: ProductPage } | { ok: false; status: number }> {
  const path = `/products${searchString({
    q: query.q?.trim() || undefined,
    origin: query.origin?.trim() || undefined,
    new: query.newFlag ? 1 : undefined,
    page: query.page > 1 ? query.page : undefined,
  })}`;
  return catalogGet<ProductPage>(path);
}
