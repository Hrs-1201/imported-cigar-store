import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-16">
      <h1 className="font-serif text-4xl">Not found</h1>
      <p className="mt-4">That page is not in the shop.</p>
      <Link href="/" className="mt-6 inline-flex text-sm underline">
        Home
      </Link>
    </main>
  );
}
