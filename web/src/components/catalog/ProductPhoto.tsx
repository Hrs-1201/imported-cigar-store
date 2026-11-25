"use client";

import Image from "next/image";
import { useState } from "react";

export function ProductPhoto({
  src,
  alt,
  brand,
  className,
}: {
  src: string | null;
  alt: string;
  brand: string;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);
  if (!src || failed) {
    return (
      <div className={`flex items-center justify-center bg-white ${className ?? ""}`}>
        <span className="font-serif text-5xl text-gold/70" aria-hidden>
          {brand.slice(0, 1)}
        </span>
      </div>
    );
  }
  return (
    <div className={`relative overflow-hidden bg-white ${className ?? ""}`}>
      <Image
        src={src}
        alt={alt}
        fill
        unoptimized
        className="object-contain p-6"
        onError={() => setFailed(true)}
      />
    </div>
  );
}
