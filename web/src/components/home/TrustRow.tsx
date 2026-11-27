import { IndianRupee, ScrollText, Shield, Truck, UserCheck, Warehouse, type LucideIcon } from "lucide-react";

const CARDS: { title: string; body: string; icon: LucideIcon }[] = [
  {
    title: "Shipping across India",
    body: "Discreet packing. We ship only where the sale is lawful.",
    icon: Truck,
  },
  {
    title: "Clear pricing",
    body: "The price on the card is the price you pay for that unit.",
    icon: IndianRupee,
  },
  {
    title: "Looked-after stock",
    body: "Cigars are kept in controlled storage before they ship.",
    icon: Warehouse,
  },
  {
    title: "Account checkout",
    body: "Orders are placed from a verified 21+ account.",
    icon: UserCheck,
  },
  {
    title: "21+ only",
    body: "We do not sell to anyone under 21.",
    icon: Shield,
  },
  {
    title: "Named sources",
    body: "Products list the brand and origin the admin entered.",
    icon: ScrollText,
  },
];

export function TrustRow() {
  return (
    <section id="home-trust" aria-labelledby="home-trust-title" className="min-w-0">
      <h2 id="home-trust-title" className="sr-only">
        How the shop sells
      </h2>
      <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CARDS.map((card) => (
          <li key={card.title} className="min-w-0 rounded-[1.75rem] border border-gold bg-white px-5 py-6">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-gold/50 text-gold">
              <card.icon size={18} aria-hidden />
            </span>
            <h3 className="mt-4 font-serif text-xl">{card.title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{card.body}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
