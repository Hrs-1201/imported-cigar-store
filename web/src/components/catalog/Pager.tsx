import Link from "next/link";

import { searchString } from "@/lib/catalog";

export function Pager({
  pathname,
  params,
  page,
  pageSize,
  total,
}: {
  pathname: string;
  params: Record<string, string | undefined>;
  page: number;
  pageSize: number;
  total: number;
}) {
  if (total <= pageSize) return null;
  const pages = Math.ceil(total / pageSize);
  const href = (nextPage: number) =>
    `${pathname}${searchString({ ...params, page: nextPage > 1 ? nextPage : undefined })}`;
  return (
    <nav className="mt-10 flex items-center justify-between text-sm" aria-label="Pages">
      {page > 1 ? (
        <Link href={href(page - 1)} className="underline">
          Previous
        </Link>
      ) : (
        <span />
      )}
      <span className="text-muted">
        Page {page} of {pages}
      </span>
      {page < pages ? (
        <Link href={href(page + 1)} className="underline">
          Next
        </Link>
      ) : (
        <span />
      )}
    </nav>
  );
}
