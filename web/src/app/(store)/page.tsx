import { BrandsRow } from "@/components/home/BrandsRow";
import { FoundersSelection } from "@/components/home/FoundersSelection";
import { Hero } from "@/components/home/Hero";
import { NewArrivals } from "@/components/home/NewArrivals";
import { Origins } from "@/components/home/Origins";
import { ShopNote } from "@/components/home/ShopNote";
import { TrustRow } from "@/components/home/TrustRow";
import { loadBrands, loadFeatured, loadNewArrivals } from "@/lib/catalog";

export default async function HomePage() {
  const [brands, featured, arrivals] = await Promise.all([loadBrands(), loadFeatured(), loadNewArrivals()]);

  return (
    <main className="overflow-x-clip">
      <Hero />
      <div className="mx-auto flex w-full min-w-0 max-w-[1160px] flex-col gap-20 px-4 pt-16 pb-20 md:gap-24 md:pt-24 md:pb-24">
        <TrustRow />
        <BrandsRow result={brands} />
        <FoundersSelection result={featured} />
        <ShopNote />
        <Origins />
        <NewArrivals result={arrivals} />
        <p id="home-later" className="text-center text-sm text-muted">
          Sampler packs and gift packs are coming.
        </p>
      </div>
    </main>
  );
}
