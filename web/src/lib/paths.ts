/** A same-app path. Rejects protocol-relative and backslash URLs. */
export function safeNextPath(value: string | null): string | null {
  if (!value || !value.startsWith("/") || value.startsWith("//") || value.startsWith("/\\")) {
    return null;
  }
  if (value.includes("\\")) return null;
  return value;
}
