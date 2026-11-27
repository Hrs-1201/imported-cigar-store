"use client";

import { ChevronRight } from "lucide-react";
import { useRef } from "react";

import { ProductCard } from "@/components/catalog/ProductCard";
import type { ProductCard as ProductCardData } from "@/types/api";

const CARD =
  "w-[82%] max-w-[82%] min-w-0 shrink-0 snap-start sm:w-[calc(50%-0.5rem)] sm:max-w-[calc(50%-0.5rem)] lg:w-[calc((100%-2rem)/3)] lg:max-w-[calc((100%-2rem)/3)]";

export function ProductCarousel({ products, label }: { products: ProductCardData[]; label: string }) {
  const scroller = useRef<HTMLUListElement>(null);

  function next() {
    const el = scroller.current;
    if (!el) return;
    const card = el.querySelector("li");
    const styles = window.getComputedStyle(el);
    const gap = Number.parseFloat(styles.columnGap || styles.gap || "0") || 0;
    const amount = (card?.getBoundingClientRect().width ?? el.clientWidth) + gap;
    const atEnd = el.scrollLeft + el.clientWidth >= el.scrollWidth - 4;
    el.scrollTo({ left: atEnd ? 0 : el.scrollLeft + amount, behavior: "smooth" });
  }

  return (
    <div className="relative min-w-0">
      <ul ref={scroller} className="flex snap-x snap-mandatory gap-4 overflow-x-auto scroll-smooth pb-3">
        {products.map((product) => (
          <li key={product.id} className={CARD}>
            <ProductCard product={product} />
          </li>
        ))}
      </ul>
      <button
        type="button"
        aria-label={label}
        onClick={next}
        className="absolute top-[22%] right-1 inline-flex h-11 w-11 items-center justify-center rounded-full border border-ink bg-paper shadow-sm"
      >
        <ChevronRight size={18} aria-hidden />
      </button>
    </div>
  );
}
