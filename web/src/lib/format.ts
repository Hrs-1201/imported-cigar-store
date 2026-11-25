export function formatInr(amount: string): string {
  const numeric = Number(amount);
  if (!Number.isFinite(numeric)) return amount;
  const fraction = amount.includes(".") ? (amount.split(".")[1] ?? "") : "";
  const showPaise = fraction.length > 0 && !/^0+$/.test(fraction);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: showPaise ? 2 : 0,
    maximumFractionDigits: showPaise ? 2 : 0,
  }).format(numeric);
}

export function phrase(value: string): string {
  const text = value.replaceAll("_", " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function smokingTime(min: number | null, max: number | null): string | null {
  if (min != null && max != null) {
    return min === max ? `${min} min` : `${min}–${max} min`;
  }
  if (min != null) return `${min} min`;
  if (max != null) return `${max} min`;
  return null;
}

export function scoreLabel(score: string): string {
  return score.endsWith(".0") ? score.slice(0, -2) : score;
}

export function boxLine(units: number | null, price: string | null): string | null {
  if (units == null && price == null) return null;
  const parts: string[] = [];
  if (units != null) parts.push(`Box of ${units}`);
  if (price != null) parts.push(formatInr(price));
  return parts.join(" · ");
}
