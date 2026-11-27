import Link from "next/link";

export function ShopNote() {
  return (
    <section id="home-note" aria-labelledby="home-note-title" className="min-w-0">
      <div className="grid items-center gap-10 md:grid-cols-2">
        <div className="mx-auto flex aspect-[3/4] w-full max-w-xs items-center justify-center rounded-[2rem] border border-gold/50 bg-[#efe2c9] md:max-w-sm">
          <p className="font-serif text-6xl tracking-wide sm:text-7xl" aria-hidden>
            <span className="text-ink">A</span>
            <span className="text-gold">&amp;</span>
            <span className="text-ink">C</span>
          </p>
        </div>
        <div className="min-w-0">
          <h2 id="home-note-title" className="text-[11px] tracking-[0.18em] text-gold uppercase">
            A note from the shop
          </h2>
          <p className="mt-5 text-base leading-7 sm:text-lg">
            Ash &amp; Cedar is a shop for people who already know they want a proper cigar, a specific cigarette, or a
            tool that works. We list what we can actually ship, with the format and the price on the card. If you want
            help choosing, write to us.
          </p>
          <p className="mt-6 font-script text-5xl text-gold">Ash &amp; Cedar</p>
          <p className="text-[11px] tracking-[0.18em] uppercase">The shop</p>
          <Link href="/contact" className="mt-6 inline-flex rounded-full border border-ink px-5 py-2.5 text-sm">
            Write to the shop
          </Link>
        </div>
      </div>
    </section>
  );
}
