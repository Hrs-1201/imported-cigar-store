"use client";

import Link from "next/link";

import { useAuth } from "@/components/auth/AuthProvider";

function firstName(fullName: string): string {
  const [name] = fullName.trim().split(/\s+/);
  return name || fullName;
}

export function AnnouncementBar() {
  const { ready, user } = useAuth();
  const href = user?.role === "admin" ? "/admin" : "/account";
  const label = user ? firstName(user.full_name) : "Login";

  return (
    <div className="border-b border-gold/30 bg-paper">
      <div className="mx-auto flex w-full max-w-[1160px] items-center gap-3 px-3 py-2 sm:px-4">
        <div className="min-w-0 flex-1 text-center text-[10px] leading-4 tracking-[0.12em] text-gold uppercase sm:text-[11px] sm:tracking-[0.16em]">
          <p>AUTHENTIC IMPORTED STOCK · DELIVERY ACROSS INDIA WHERE LAWFUL</p>
          <p>ADULTS 21+ · DUTY-PAID GOODS ONLY</p>
        </div>
        {ready ? (
          <Link
            href={user ? href : "/login"}
            className="inline-flex max-w-28 shrink-0 truncate rounded-full border border-ink px-3 py-1 text-xs text-ink"
          >
            {label}
          </Link>
        ) : (
          <span className="inline-block h-7 w-16 shrink-0" aria-hidden />
        )}
      </div>
    </div>
  );
}
