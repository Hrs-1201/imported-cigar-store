"""Dev-only catalog of the brand lists supplied for the shop demo.

Does not run on startup. Do not point it at a production database.
Prices and sizes are demo figures. A photo is attached only when a file
for that product is already in api/storage/products/.

    python -m app.scripts.seed_demo
"""

import re
import unicodedata
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.catalog import Category, Product, ProductImage, ProductShape, Strength

_WHEN = datetime(2026, 11, 20, 9, 0, tzinfo=timezone.utc)
_NEW_BASE = datetime(2026, 11, 24, 9, 0, tzinfo=timezone.utc)

_RETIRED = (
    "DEMO-CIG-001",
    "DEMO-CIG-002",
    "DEMO-CIG-003",
    "DEMO-CIG-004",
    "DEMO-CGT-001",
    "DEMO-CGT-002",
)

# brand, line, shape, length, ring, strength, price, stock, founder rank (0 = none), new arrival
_CIGARS: dict[str, list[tuple]] = {
    "Cuba": [
        ("Cohiba", "Siglo VI", "toro", "5.90", 52, "medium_to_full", "6500.00", 1, 1, False),
        ("Montecristo", "No. 2", "figurado", "6.10", 52, "medium", "4200.00", 8, 2, False),
        ("Romeo y Julieta", "Churchill", "churchill", "7.00", 47, "medium", "2800.00", 10, 0, False),
        ("Partagás", "Serie D No. 4", "robusto", "4.90", 50, "full", "3600.00", 6, 0, False),
        ("Hoyo de Monterrey", "Epicure No. 2", "robusto", "4.90", 50, "mild_to_medium", "3200.00", 9, 0, False),
        ("H. Upmann", "Magnum 46", "robusto", "5.60", 46, "medium", "3000.00", 7, 0, False),
        ("Trinidad", "Fundadores", "lancero", "7.60", 40, "medium_to_full", "7000.00", 3, 0, False),
        ("Quintero", "Favoritos", "robusto", "4.80", 50, "medium", "1400.00", 14, 0, False),
        ("José L. Piedra", "Petit Cazadores", "corona", "4.10", 42, "medium", "900.00", 16, 0, False),
        ("Vegueros", "Entretiempos", "robusto", "5.40", 54, "medium", "1800.00", 11, 0, False),
        ("Bolívar", "Belicosos Finos", "figurado", "5.50", 52, "full", "3400.00", 5, 0, False),
        ("Punch", "Punch", "corona", "5.60", 46, "medium_to_full", "2200.00", 8, 0, False),
        ("Ramón Allones", "Specially Selected", "robusto", "4.90", 50, "medium_to_full", "2600.00", 6, 0, False),
        ("Cuaba", "Divinos", "figurado", "4.00", 43, "medium", "2400.00", 4, 0, True),
        ("Fonseca", "Cosacos", "corona", "5.40", 42, "mild", "1600.00", 9, 0, False),
        ("Quai d'Orsay", "No. 50", "robusto", "4.30", 50, "mild_to_medium", "3000.00", 5, 0, False),
        ("Rafael González", "Petit Coronas", "corona", "5.10", 42, "mild_to_medium", "1800.00", 7, 0, False),
        ("San Cristóbal de La Habana", "El Príncipe", "corona", "4.30", 42, "medium", "2500.00", 6, 0, False),
    ],
    "Dominican Republic": [
        ("Arturo Fuente", "Hemingway Short Story", "figurado", "4.00", 49, "medium", "3200.00", 6, 0, False),
        ("Davidoff", "Grand Cru No. 2", "toro", "6.00", 52, "mild_to_medium", "4800.00", 4, 3, False),
        ("La Aurora", "Preferidos", "figurado", "5.00", 54, "medium", "2600.00", 5, 0, False),
        ("Macanudo", "Vintage Maduro", "robusto", "5.00", 50, "medium", "2200.00", 8, 0, False),
        ("VegaFina", "1998", "robusto", "5.00", 50, "mild_to_medium", "1800.00", 10, 0, False),
        ("AVO", "Classic", "robusto", "5.00", 50, "medium", "2400.00", 7, 0, False),
        ("Ashton", "Cabinet Selection", "churchill", "7.00", 48, "mild", "2800.00", 4, 0, False),
        ("Don Diego", "Classic", "corona", "5.50", 42, "mild_to_medium", "1400.00", 12, 0, False),
        ("Griffin's", "Robusto", "robusto", "5.00", 50, "medium", "2000.00", 6, 0, False),
        ("La Flor Dominicana", "Ligero", "toro", "6.00", 52, "full", "3000.00", 5, 0, False),
        ("León Jimenes", "No. 5", "corona", "5.00", 42, "mild_to_medium", "1600.00", 8, 0, False),
        ("Quesada", "Tributo", "toro", "6.00", 52, "medium_to_full", "2700.00", 4, 0, False),
        ("Casa de Garcia", "Corona", "corona", "5.50", 42, "medium", "1200.00", 15, 0, False),
        ("Santa Damiana", "Classic", "robusto", "5.00", 50, "medium", "1500.00", 9, 0, False),
        ("Aging Room", "Quattro", "toro", "6.00", 52, "medium_to_full", "3400.00", 3, 0, True),
    ],
    "Nicaragua": [
        ("Padron", "1964 Anniversary", "robusto", "5.00", 50, "full", "4500.00", 4, 4, False),
        ("Oliva", "Serie V", "robusto", "5.00", 50, "full", "2800.00", 8, 0, False),
        ("AJ Fernandez", "New World", "toro", "6.00", 52, "medium_to_full", "1900.00", 11, 0, False),
        ("My Father", "Le Bijou", "toro", "6.00", 52, "full", "3200.00", 5, 0, False),
        ("Joya de Nicaragua", "Antaño", "robusto", "5.00", 50, "full", "2100.00", 7, 0, False),
        ("Drew Estate", "Liga Privada", "toro", "6.00", 52, "full", "3600.00", 4, 0, False),
        ("Plasencia", "Alma Fuerte", "toro", "6.00", 54, "medium_to_full", "3400.00", 3, 0, False),
        ("Perdomo", "10th Anniversary", "robusto", "5.00", 50, "medium", "2000.00", 9, 0, False),
        ("Tatuaje", "Havana VI", "robusto", "5.00", 50, "medium_to_full", "2300.00", 6, 0, False),
        ("Foundation", "Tabernacle", "robusto", "5.00", 50, "full", "2700.00", 5, 0, False),
        ("La Aroma de Cuba", "Mi Amor", "robusto", "5.00", 50, "medium_to_full", "2200.00", 6, 0, False),
        ("Aganorsa Leaf", "Rare Leaf", "toro", "6.00", 52, "medium_to_full", "2500.00", 4, 0, False),
        ("Nub", "Connecticut", "robusto", "4.00", 60, "mild", "1600.00", 10, 0, True),
        ("5 Vegas", "Classic", "robusto", "5.00", 50, "medium", "1300.00", 12, 0, False),
        ("Mombacho", "Liga Maestro", "toro", "6.00", 52, "medium_to_full", "2400.00", 5, 0, False),
    ],
    "Honduras": [
        ("Camacho", "Corojo", "robusto", "5.00", 50, "full", "2200.00", 7, 0, False),
        ("Alec Bradley", "Prensado", "toro", "6.00", 52, "medium_to_full", "2400.00", 6, 0, False),
        ("Flor de Copan", "Classic", "corona", "5.50", 42, "medium", "1400.00", 8, 0, False),
        ("Rocky Patel", "Decade", "toro", "6.00", 52, "medium", "2600.00", 0, 0, True),
        ("Aladino", "Corojo", "robusto", "5.00", 50, "medium_to_full", "2000.00", 5, 0, False),
        ("CLE", "Corojo", "robusto", "5.00", 50, "medium_to_full", "2100.00", 4, 0, False),
        ("Baccarat", "The Game", "robusto", "5.00", 50, "medium", "1500.00", 9, 0, False),
        ("CAO", "Brazilia", "robusto", "5.00", 50, "medium_to_full", "1800.00", 8, 0, False),
        ("Eiroa", "Classic", "robusto", "5.00", 50, "medium", "2300.00", 4, 0, False),
        ("Gran Habano", "Corojo", "robusto", "5.00", 50, "medium_to_full", "1700.00", 7, 0, False),
        ("Cavalier Genève", "White Series", "toro", "6.00", 52, "medium", "2800.00", 3, 0, False),
        ("Punch", "Rare Corojo", "robusto", "5.00", 50, "medium_to_full", "1600.00", 6, 0, False),
        ("Hoyo de Monterrey", "Excalibur", "churchill", "7.00", 48, "medium", "1900.00", 5, 0, False),
        ("Villa Zamorano", "Classic", "corona", "5.50", 42, "medium", "1300.00", 10, 0, False),
        ("Maya Selva", "Flor de Selva", "robusto", "5.00", 50, "medium", "2100.00", 4, 0, False),
    ],
}

_CIGARETTES: dict[str, list[str]] = {
    "Russia": [
        "Russian Style",
        "Play",
        "Donskoy Tabak",
        "Java",
        "Belomorkanal",
        "Alliance",
        "21 Vek",
        "Kiss",
        "Maxim",
        "Balkan Star",
        "Manchester",
        "Captain Jack",
        "LD",
        "Sobranie",
        "Winston",
        "Camel",
    ],
    "China": [
        "Chunghwa (Zhonghua)",
        "Panda",
        "Hongtashan",
        "Baisha",
        "Liqun",
        "Yuxi",
        "Honghe",
        "Huanghelou",
        "Nanjing",
        "Furongwang",
        "Yunyan",
        "Zhongnanhai",
        "Double Happiness (Shuangxi)",
        "Suyan",
        "Huangshan",
        "Golden Leaf",
        "Septwolves",
        "Taishan",
        "Diamond",
        "Lanzhou",
    ],
    "Japan": [
        "Mevius",
        "Seven Stars",
        "Peace",
        "Hope",
        "Hi-Lite",
        "Cabin",
        "Caster",
        "Pianissimo",
        "Sakura",
        "Camel",
        "Winston",
        "Natural American Spirit",
    ],
    "Ukraine": [
        "Pryluky",
        "Prima",
        "Sk",
        "Estrada",
        "Barge",
        "Derzhavna",
        "Grelka",
        "Kyiv",
        "Marvel",
        "Compliment",
        "Strong",
        "Lifa",
        "Vogue",
        "Kent",
        "Rothmans",
        "Davidoff",
        "Monte Carlo",
        "Glamour",
    ],
    "United Kingdom": [
        "Benson & Hedges",
        "Sterling",
        "Mayfair",
        "Kensitas Club",
        "American Spirit",
        "Winston",
        "Sovereign",
        "Silk Cut",
        "Camel",
        "Embassy",
        "Player's",
        "Lambert & Butler",
        "Richmond",
        "Pall Mall",
        "Rothmans",
        "Dunhill",
        "Vogue",
        "JPS",
    ],
    "Thailand": [
        "Samit 90",
        "Krung Thong 90",
        "Krong Thip 90",
        "Sai Fon 90",
        "Wonder S",
        "SMS",
        "Goal",
        "Line",
        "Krong Thip 7.1 S",
        "Line 7.1",
        "Mage F1",
        "Mage F2",
        "Blackjack Maroon X2",
    ],
}

_COUNTRY_CODE = {
    "Cuba": "CUB",
    "Dominican Republic": "DOM",
    "Nicaragua": "NIC",
    "Honduras": "HON",
    "Russia": "RUS",
    "China": "CHN",
    "Japan": "JPN",
    "Ukraine": "UKR",
    "United Kingdom": "GBR",
    "Thailand": "THA",
}

_SMOKE = {
    "robusto": (40, 55),
    "toro": (50, 70),
    "churchill": (60, 80),
    "lancero": (60, 75),
    "corona": (30, 45),
    "figurado": (45, 60),
}

_INTENSITY = {
    "mild": 1,
    "mild_to_medium": 2,
    "medium": 3,
    "medium_to_full": 4,
    "full": 5,
}

_PACK_STRENGTH = ("mild", "medium", "medium_to_full", "full")

# Files the shop already placed in api/storage/products/.
_IMAGES = {
    ("cigars", "Macanudo", "Vintage Maduro"): [
        ("macanudo-vintage-maduro-cigar.jpeg", "Macanudo Vintage Maduro"),
    ],
    ("cigarettes", "Sobranie", "Russia"): [
        ("sobranie_one.jpeg", "Sobranie"),
        ("sobranie_two.jpeg", "Sobranie, second view"),
    ],
}


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def _images_for(category: str, brand: str, country: str, name: str) -> list[dict]:
    key = (category, brand, name if category == "cigars" else country)
    rows = _IMAGES.get(key, [])
    return [
        {
            "storage_key": filename,
            "alt_text": alt,
            "sort_order": index,
            "is_primary": index == 0,
        }
        for index, (filename, alt) in enumerate(rows)
    ]


def _catalog() -> list[dict]:
    products: list[dict] = []
    new_index = 0
    for country, rows in _CIGARS.items():
        code = _COUNTRY_CODE[country]
        for index, row in enumerate(rows, start=1):
            brand, name, shape, length, ring, strength, price, stock, founder_rank, is_new = row
            smoke_min, smoke_max = _SMOKE[shape]
            price_amount = Decimal(price)
            created_at = _WHEN
            if is_new:
                new_index += 1
                created_at = _NEW_BASE + timedelta(hours=new_index)
            products.append(
                {
                    "category_slug": "cigars",
                    "sku": f"CIG-{code}-{index:03d}",
                    "slug": _slug(f"{brand}-{name}"),
                    "name": name,
                    "brand": brand,
                    "subtype": "habano" if country == "Cuba" else "new_world",
                    "short_description": f"{name} from {brand}. {country}.",
                    "description": f"{brand} {name}. Listed as a single from {country}.",
                    "price_inr": price_amount,
                    "box_price_inr": price_amount * 25,
                    "units_per_box": 25,
                    "stock_qty": stock,
                    "low_stock_threshold": 2,
                    "origin_country": country,
                    "origin_label": country,
                    "smoking_time_min_minutes": smoke_min,
                    "smoking_time_max_minutes": smoke_max,
                    "intensity": _INTENSITY[strength],
                    "strength": Strength(strength),
                    "shape": ProductShape(shape),
                    "length_inches": Decimal(length),
                    "ring_gauge": ring,
                    "is_founder_pick": founder_rank > 0,
                    "founder_rank": founder_rank or None,
                    "is_new_arrival": is_new,
                    "is_published": True,
                    "created_at": created_at,
                    "updated_at": created_at,
                    "images": _images_for("cigars", brand, country, name),
                }
            )
    for country, brands in _CIGARETTES.items():
        code = _COUNTRY_CODE[country]
        for index, brand in enumerate(brands, start=1):
            strength = _PACK_STRENGTH[(index - 1) % len(_PACK_STRENGTH)]
            is_new = brand in {"Sobranie", "Mevius", "Chunghwa (Zhonghua)", "Benson & Hedges"}
            created_at = _WHEN
            if is_new:
                new_index += 1
                created_at = _NEW_BASE + timedelta(hours=new_index)
            price = Decimal(360 + (index * 15) + (len(country) % 5) * 10)
            products.append(
                {
                    "category_slug": "cigarettes",
                    "sku": f"CGT-{code}-{index:03d}",
                    "slug": _slug(f"{brand}-{country}"),
                    "name": brand,
                    "brand": brand,
                    "subtype": "pack",
                    "short_description": f"Imported pack. {country}.",
                    "description": f"{brand}, packed for the {country} listing.",
                    "price_inr": price,
                    "units_per_pack": 20,
                    "stock_qty": 0 if brand == "Belomorkanal" else 6 + (index % 10),
                    "origin_country": country,
                    "origin_label": country,
                    "strength": Strength(strength),
                    "is_new_arrival": is_new,
                    "is_published": True,
                    "created_at": created_at,
                    "updated_at": created_at,
                    "images": _images_for("cigarettes", brand, country, brand),
                }
            )
    products.extend(
        [
            {
                "category_slug": "cigars",
                "sku": "DEMO-CIG-HIDDEN",
                "slug": "hidden-drawer-stick",
                "name": "Hidden Drawer Stick",
                "brand": "Sample Habano",
                "subtype": "habano",
                "short_description": "Unpublished on purpose. The shop must not list this.",
                "description": "This row stays hidden so a published filter can be checked by hand.",
                "price_inr": Decimal("999.00"),
                "stock_qty": 9,
                "origin_country": "Cuba",
                "origin_label": "Should not be visible",
                "is_published": False,
                "images": [],
            },
            {
                "category_slug": "lighters",
                "sku": "DEMO-LIT-001",
                "slug": "demo-torch-lighter",
                "name": "Demo Torch Lighter",
                "brand": "Sample Flame",
                "subtype": "torch",
                "short_description": "Fictional lighter. Not a real product.",
                "description": "A made-up torch so the lighters page is not empty.",
                "price_inr": Decimal("3200.00"),
                "stock_qty": 3,
                "origin_country": "USA",
                "origin_label": "Made in USA",
                "is_published": True,
                "images": [],
            },
            {
                "category_slug": "accessories",
                "sku": "DEMO-ACC-001",
                "slug": "demo-guillotine-cutter",
                "name": "Demo Guillotine Cutter",
                "brand": "Sample Edge",
                "subtype": "cutter",
                "short_description": "A fictional cutter for the demo shelf.",
                "description": "Not a real cutter. It exists so the accessories grid has a card.",
                "price_inr": Decimal("900.00"),
                "stock_qty": 5,
                "is_published": True,
                "images": [],
            },
            {
                "category_slug": "accessories",
                "sku": "DEMO-ACC-002",
                "slug": "demo-ceramic-ashtray",
                "name": "Demo Ceramic Ashtray",
                "brand": "Sample Rest",
                "subtype": "ashtray",
                "short_description": "A fictional ashtray for the demo shelf.",
                "description": "Not a real ashtray. It exists so the accessories grid has a second card.",
                "price_inr": Decimal("750.00"),
                "stock_qty": 4,
                "is_published": True,
                "images": [],
            },
        ]
    )
    slugs = [item["slug"] for item in products]
    skus = [item["sku"] for item in products]
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("Demo catalog has a duplicate slug.")
    if len(skus) != len(set(skus)):
        raise RuntimeError("Demo catalog has a duplicate SKU.")
    return products


_PRODUCTS = _catalog()


def _attach_images(db: Session, product: Product, images: list[dict]) -> int:
    existing = {image.storage_key for image in product.images}
    added = 0
    for image in images:
        if image["storage_key"] in existing:
            continue
        db.add(
            ProductImage(
                product_id=product.id,
                storage_key=image["storage_key"],
                public_path=f"/api/v1/media/products/{image['storage_key']}",
                alt_text=image["alt_text"],
                sort_order=image["sort_order"],
                is_primary=image["is_primary"],
            )
        )
        added += 1
    return added


def seed_demo(db: Session) -> tuple[list[str], int]:
    retired = list(db.scalars(select(Product).where(Product.sku.in_(_RETIRED))))
    for row in retired:
        db.delete(row)
    if retired:
        db.flush()
    created: list[str] = []
    images_added = 0
    for spec in _PRODUCTS:
        images = spec["images"]
        product = db.scalar(select(Product).where(Product.sku == spec["sku"]))
        if product is None:
            category = db.scalar(select(Category).where(Category.slug == spec["category_slug"]))
            if category is None:
                raise RuntimeError(f"Missing category {spec['category_slug']}. Run alembic upgrade head first.")
            fields = {
                key: value
                for key, value in spec.items()
                if key not in {"category_slug", "images"}
            }
            product = Product(category_id=category.id, **fields)
            db.add(product)
            db.flush()
            created.append(spec["sku"])
        images_added += _attach_images(db, product, images)
    db.commit()
    return created, images_added


def main() -> None:
    database = make_url(get_settings().database_url).database or ""
    if database.endswith("_test"):
        raise SystemExit("Refusing to seed a test database.")
    db = SessionLocal()
    try:
        created, images_added = seed_demo(db)
    finally:
        db.close()
    print(
        f"Dev catalog: {len(created)} new products, {images_added} images attached. "
        "Prices are demo figures."
    )


if __name__ == "__main__":
    main()
