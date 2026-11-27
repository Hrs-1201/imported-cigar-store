"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

type SlideAction = {
  href: string;
  label: string;
  tone: "solid" | "outline";
};

type Slide = {
  id: string;
  eyebrow: string;
  lead: string;
  script: string;
  close: string;
  note?: string;
  image: string;
  alt: string;
  actions: SlideAction[];
};

const SLIDES: Slide[] = [
  {
    id: "hour",
    eyebrow: "Imported cigars, cigarettes & accessories",
    lead: "The right hour",
    script: "for a good",
    close: "Cigar",
    note: "Age-verified delivery. 21+ only.",
    image: "/home/hero-cigars.svg",
    alt: "A drawn still life of two cigars on warm paper",
    actions: [
      { href: "/cigars", label: "Shop cigars", tone: "solid" },
      { href: "/accessories", label: "Lighters & accessories", tone: "outline" },
    ],
  },
  {
    id: "drawer",
    eyebrow: "Cigarettes",
    lead: "Packs chosen",
    script: "for the",
    close: "Drawer",
    image: "/home/hero-cigarettes.svg",
    alt: "A drawn still life of a plain cigarette pack",
    actions: [{ href: "/cigarettes", label: "Shop cigarettes", tone: "solid" }],
  },
  {
    id: "tools",
    eyebrow: "The tools",
    lead: "Cutters, ashtrays",
    script: "and a",
    close: "Flame",
    image: "/home/hero-tools.svg",
    alt: "A drawn still life of a cutter, an ashtray, and a flame",
    actions: [
      { href: "/accessories", label: "Shop accessories", tone: "solid" },
      { href: "/lighters", label: "Shop lighters", tone: "outline" },
    ],
  },
];

function actionClass(tone: SlideAction["tone"]): string {
  if (tone === "solid") return "rounded-full bg-ink px-5 py-2.5 text-sm text-white";
  return "rounded-full border border-ink px-5 py-2.5 text-sm text-ink";
}

export function Hero() {
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const slide = SLIDES[index] ?? SLIDES[0];

  useEffect(() => {
    if (paused) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setInterval(() => {
      setIndex((current) => (current + 1) % SLIDES.length);
    }, 7000);
    return () => window.clearInterval(timer);
  }, [paused, index]);

  function go(next: number) {
    setIndex((next + SLIDES.length) % SLIDES.length);
  }

  return (
    <section
      id="home-hero"
      aria-roledescription="carousel"
      aria-label="Shop highlights"
      className="overflow-x-clip"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocusCapture={() => setPaused(true)}
      onBlurCapture={(event) => {
        const next = event.relatedTarget;
        if (next instanceof Node && event.currentTarget.contains(next)) return;
        setPaused(false);
      }}
    >
      <div className="mx-auto grid w-full max-w-[1160px] items-center gap-10 px-4 py-12 md:grid-cols-2 md:py-16">
        <div className="min-w-0">
          <p className="text-[11px] tracking-[0.16em] text-gold uppercase">{slide.eyebrow}</p>
          <h1 className="mt-4 max-w-full text-balance">
            <span className="block font-serif text-[1.85rem] leading-[1.05] uppercase sm:text-5xl lg:text-6xl">
              {slide.lead}
            </span>
            <span className="mt-1 block font-script text-5xl leading-none text-gold sm:text-6xl">{slide.script}</span>
            <span className="mt-1 block font-serif text-[1.85rem] leading-[1.05] uppercase sm:text-5xl lg:text-6xl">
              {slide.close}
            </span>
          </h1>
          {slide.note ? <p className="mt-5 text-sm text-muted sm:text-base">{slide.note}</p> : null}
          <div className="mt-6 flex flex-wrap gap-3">
            {slide.actions.map((action) => (
              <Link key={action.href + action.label} href={action.href} className={actionClass(action.tone)}>
                {action.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="min-w-0">
          <div className="relative mx-auto aspect-[4/5] w-full max-w-md overflow-hidden rounded-[2rem] border border-gold/40 md:max-w-none">
            <Image
              src={slide.image}
              alt={slide.alt}
              fill
              unoptimized
              sizes="(min-width: 768px) 540px, 100vw"
              className="object-cover"
            />
          </div>
        </div>
      </div>
      <div className="flex items-center justify-center gap-4 px-4 pb-2">
        <button
          type="button"
          className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-ink/30"
          aria-label="Previous slide"
          onClick={() => go(index - 1)}
        >
          <ChevronLeft size={18} />
        </button>
        <div className="flex items-center gap-2" role="group" aria-label="Choose a slide">
          {SLIDES.map((item, itemIndex) => (
            <button
              key={item.id}
              type="button"
              aria-label={`Show slide ${itemIndex + 1} of ${SLIDES.length}`}
              aria-current={itemIndex === index ? "true" : undefined}
              className={`h-2 rounded-full ${itemIndex === index ? "w-6 bg-ink" : "w-2 bg-ink/30"}`}
              onClick={() => go(itemIndex)}
            />
          ))}
        </div>
        <button
          type="button"
          className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-ink/30"
          aria-label="Next slide"
          onClick={() => go(index + 1)}
        >
          <ChevronRight size={18} />
        </button>
      </div>
    </section>
  );
}
