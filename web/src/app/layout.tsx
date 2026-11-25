import type { Metadata } from "next";
import { Fraunces, Great_Vibes, Outfit } from "next/font/google";

import { AgeGate } from "@/components/age-gate/AgeGate";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { brand } from "@/lib/brand";

import "./globals.css";

const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });
const fraunces = Fraunces({ subsets: ["latin"], variable: "--font-fraunces" });
const script = Great_Vibes({ weight: "400", subsets: ["latin"], variable: "--font-great-vibes" });

export const metadata: Metadata = {
  title: {
    default: brand.name,
    template: `%s · ${brand.name}`,
  },
  description: brand.tagline,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${outfit.variable} ${fraunces.variable} ${script.variable} h-full antialiased`}>
      <body className="min-h-full bg-paper font-sans text-ink">
        <AgeGate>
          <AuthProvider>{children}</AuthProvider>
        </AgeGate>
      </body>
    </html>
  );
}
