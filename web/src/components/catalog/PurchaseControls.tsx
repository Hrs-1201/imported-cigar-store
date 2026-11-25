"use client";

import { Minus, Plus, ShoppingBag } from "lucide-react";
import { useState } from "react";

export function PurchaseControls({ stockQty, inStock }: { stockQty: number; inStock: boolean }) {
  const [quantity, setQuantity] = useState(1);
  const max = inStock ? Math.max(stockQty, 1) : 1;

  return (
    <div className="mt-5 space-y-3">
      <div className="flex items-center justify-center gap-4">
        <button
          type="button"
          aria-label="Decrease quantity"
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-ink/30 disabled:opacity-40"
          disabled={quantity <= 1}
          onClick={() => setQuantity((current) => Math.max(1, current - 1))}
        >
          <Minus size={14} />
        </button>
        <span className="min-w-6 text-center tabular-nums" aria-live="polite">
          {quantity}
        </span>
        <button
          type="button"
          aria-label="Increase quantity"
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-ink/30 disabled:opacity-40"
          disabled={!inStock || quantity >= max}
          onClick={() => setQuantity((current) => Math.min(max, current + 1))}
        >
          <Plus size={14} />
        </button>
      </div>
      <button
        type="button"
        disabled
        className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-ink px-5 py-2.5 text-sm text-white disabled:cursor-not-allowed disabled:opacity-60"
      >
        <ShoppingBag size={16} aria-hidden />
        {inStock ? "Add" : "Out of stock"}
      </button>
      <p className="text-center text-xs text-muted">Sign in to add — cart opens in a later phase.</p>
    </div>
  );
}
