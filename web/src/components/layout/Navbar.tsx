"use client";

import { Menu, Search, ShoppingBag, User, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useAuth } from "@/components/auth/AuthProvider";
import { brand } from "@/lib/brand";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/cigars", label: "Cigars" },
  { href: "/cigarettes", label: "Cigarettes" },
  { href: "/lighters", label: "Lighters" },
  { href: "/accessories", label: "Accessories" },
  { href: "/contact", label: "Contact Us" },
];

function isCurrent(href: string, pathname: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Navbar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const [menuPath, setMenuPath] = useState<string | null>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const menuOpen = menuPath === pathname;

  useEffect(() => {
    if (searchOpen) searchRef.current?.focus();
  }, [searchOpen]);

  function onSearch() {
    setMenuPath(null);
  }

  const linkClass = (href: string) =>
    `text-[11px] tracking-[0.16em] uppercase ${
      isCurrent(href, pathname) ? "font-semibold text-ink" : "font-medium text-ink/70"
    }`;

  return (
    <header className="border-b border-gold/40 bg-paper">
      <div className="mx-auto grid w-full max-w-[1160px] grid-cols-[auto_1fr_auto] items-center gap-2 px-3 py-3 sm:px-4">
        <div className="flex items-center gap-1">
          <button
            type="button"
            className="inline-flex h-9 w-9 items-center justify-center min-[960px]:hidden"
            aria-expanded={menuOpen}
            aria-controls="store-menu"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            onClick={() => setMenuPath((current) => (current === pathname ? null : pathname))}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <Link href="/" className="font-script text-[1.65rem] leading-none text-gold sm:text-4xl">
            {brand.name}
          </Link>
        </div>
        <nav className="hidden items-center justify-center gap-5 min-[960px]:flex" aria-label="Shop">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} className={linkClass(link.href)} aria-current={isCurrent(link.href, pathname) ? "page" : undefined}>
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center justify-end gap-0.5">
          <button
            type="button"
            className="inline-flex h-9 w-9 items-center justify-center"
            aria-label="Search"
            aria-expanded={searchOpen}
            onClick={() => setSearchOpen((open) => !open)}
          >
            <Search size={18} />
          </button>
          <Link
            href={user ? "/account" : "/login"}
            className="inline-flex h-9 w-9 items-center justify-center"
            aria-label="Account"
          >
            <User size={18} />
          </Link>
          <Link href="/cart" className="inline-flex h-9 w-9 items-center justify-center" aria-label="Cart">
            <ShoppingBag size={18} />
          </Link>
        </div>
      </div>
      {menuOpen ? (
        <nav id="store-menu" className="border-t border-gold/30 px-4 py-4 min-[960px]:hidden" aria-label="Shop">
          <ul className="flex flex-col gap-3">
            {LINKS.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className={linkClass(link.href)} onClick={() => setMenuPath(null)}>
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      ) : null}
      {searchOpen ? (
        <form action="/search" className="border-t border-gold/30 px-3 py-3 sm:px-4" onSubmit={onSearch}>
          <div className="mx-auto flex w-full max-w-[1160px] gap-2">
            <label className="sr-only" htmlFor="nav-search">
              Search products
            </label>
            <input
              id="nav-search"
              name="q"
              ref={searchRef}
              placeholder="Search by name or brand"
              className="min-w-0 flex-1 rounded-full border border-gold/40 bg-white px-4 py-2 text-sm outline-none focus:border-ink"
            />
            <button type="submit" className="shrink-0 rounded-full bg-ink px-4 text-sm text-white">
              Search
            </button>
          </div>
        </form>
      ) : null}
    </header>
  );
}
