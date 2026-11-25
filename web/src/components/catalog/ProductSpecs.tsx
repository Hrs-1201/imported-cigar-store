import type { ReactNode } from "react";

import { boxLine, phrase, smokingTime } from "@/lib/format";
import type { ProductCard } from "@/types/api";

type Cell = { label: string; value: ReactNode } | null;

function Intensity({ value }: { value: number }) {
  return (
    <span className="inline-flex gap-1" aria-label={`Intensity ${value} of 5`}>
      {Array.from({ length: 5 }, (_, index) => (
        <span key={index} className={`h-1.5 w-1.5 rounded-full ${index < value ? "bg-ink" : "bg-ink/20"}`} />
      ))}
    </span>
  );
}

function SpecGrid({ rows }: { rows: Array<[Cell, Cell]> }) {
  const visible = rows.filter((row) => row[0] || row[1]);
  if (visible.length === 0) return null;
  return (
    <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 text-xs">
      {visible.flatMap((row, index) =>
        row.map((cell, cellIndex) => (
          <div key={`${index}-${cellIndex}`} className="min-w-0">
            {cell ? (
              <>
                <dt className="tracking-[0.14em] text-muted uppercase">{cell.label}</dt>
                <dd className="mt-1 break-words text-sm text-ink">{cell.value}</dd>
              </>
            ) : null}
          </div>
        )),
      )}
    </dl>
  );
}

function Lines({ items }: { items: Array<string | null> }) {
  const visible = items.filter((item): item is string => Boolean(item));
  if (visible.length === 0) return null;
  return (
    <ul className="mt-4 space-y-1 text-sm text-muted">
      {visible.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function ProductSpecs({ product }: { product: ProductCard }) {
  if (product.category_slug === "cigars") {
    const time = smokingTime(product.smoking_time_min_minutes, product.smoking_time_max_minutes);
    const box = boxLine(product.units_per_box, product.box_price_inr);
    return (
      <SpecGrid
        rows={[
          [
            time ? { label: "Smoking time", value: time } : null,
            product.intensity != null ? { label: "Intensity", value: <Intensity value={product.intensity} /> } : null,
          ],
          [
            product.strength ? { label: "Strength", value: phrase(product.strength) } : null,
            product.shape ? { label: "Shape", value: phrase(product.shape) } : null,
          ],
          [
            product.size_label ? { label: "Size", value: product.size_label } : null,
            box ? { label: "Box", value: box } : null,
          ],
        ]}
      />
    );
  }

  if (product.category_slug === "cigarettes") {
    return (
      <Lines
        items={[
          product.strength ? `Strength · ${phrase(product.strength)}` : null,
          product.units_per_pack != null ? `Pack of ${product.units_per_pack}` : null,
          product.origin_label,
        ]}
      />
    );
  }

  if (product.category_slug === "lighters") {
    return (
      <Lines
        items={[product.origin_label, product.subtype ? phrase(product.subtype) : null]}
      />
    );
  }

  return (
    <Lines
      items={[
        product.subtype ? phrase(product.subtype) : null,
        product.short_description,
        product.origin_label,
      ]}
    />
  );
}
