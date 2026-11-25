import { brand } from "@/lib/brand";

export default function HomePage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col items-center px-4 py-24 text-center">
      <p className="font-script text-6xl text-gold">{brand.name}</p>
      <h1 className="mt-6 font-serif text-4xl">Welcome</h1>
      <p className="mt-4 text-lg text-muted">The full home page is next.</p>
    </main>
  );
}
