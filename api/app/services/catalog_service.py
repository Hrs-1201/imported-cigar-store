import uuid
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.catalog import Product, ProductImage, ProductRating
from app.repositories.catalog_repo import CatalogRepository
from app.schemas.catalog import (
    BrandList,
    CategoryList,
    CategoryPublic,
    ProductCard,
    ProductCardList,
    ProductCardPage,
    ProductDetail,
    ProductImagePublic,
    RatingPublic,
)

_repo = CatalogRepository()
_CARD_RATINGS = 2
_LIST_CAP = 12


class CatalogNotFound(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


def list_categories(db: Session) -> CategoryList:
    rows = _repo.list_categories(db)
    return CategoryList(items=[CategoryPublic.model_validate(row) for row in rows])


def category_products(
    db: Session,
    slug: str,
    *,
    q: str | None,
    origin: str | None,
    page: int,
    page_size: int,
) -> ProductCardPage:
    category = _repo.get_category_by_slug(db, slug)
    if category is None:
        raise CatalogNotFound("Category not found")
    return _page(
        db,
        category_id=category.id,
        q=_blank_to_none(q),
        origin=_blank_to_none(origin),
        new_only=False,
        page=page,
        page_size=page_size,
    )


def search_products(
    db: Session,
    *,
    q: str | None,
    origin: str | None,
    new_only: bool,
    page: int,
    page_size: int,
) -> ProductCardPage:
    # No query and no new flag: do not dump the catalog. Origin alone does not count.
    if _blank_to_none(q) is None and not new_only:
        return ProductCardPage(items=[], total=0, page=page, page_size=page_size)
    return _page(
        db,
        category_id=None,
        q=_blank_to_none(q),
        origin=_blank_to_none(origin),
        new_only=new_only,
        page=page,
        page_size=page_size,
    )


def featured_products(db: Session) -> ProductCardList:
    rows = _repo.featured(db, limit=_LIST_CAP)
    return ProductCardList(items=[_card(row) for row in rows])


def new_arrival_products(db: Session) -> ProductCardList:
    rows = _repo.new_arrivals(db, limit=_LIST_CAP)
    return ProductCardList(items=[_card(row) for row in rows])


def list_brands(db: Session) -> BrandList:
    return BrandList(items=_repo.brands(db))


def get_product(db: Session, slug: str) -> ProductDetail:
    product = _repo.get_public_by_slug(db, slug)
    if product is None:
        raise CatalogNotFound("Product not found")
    return _detail(product)


def resolve_public_media(db: Session, filename: str) -> Path | None:
    image = _repo.get_image_by_key(db, filename)
    if image is None or image.product.deleted_at is not None or not image.product.is_published:
        return None
    root = _media_root()
    candidate = (root / filename).resolve()
    if root.resolve() not in candidate.parents:
        return None
    if not candidate.is_file():
        return None
    return candidate


def _page(
    db: Session,
    *,
    category_id: uuid.UUID | None,
    q: str | None,
    origin: str | None,
    new_only: bool,
    page: int,
    page_size: int,
) -> ProductCardPage:
    rows, total = _repo.page_public(
        db,
        category_id=category_id,
        q=q,
        origin=origin,
        new_only=new_only,
        page=page,
        page_size=page_size,
    )
    return ProductCardPage(
        items=[_card(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


def _card(product: Product) -> ProductCard:
    ratings = _ordered_ratings(product)
    visible = ratings[:_CARD_RATINGS]
    images = _ordered_images(product)
    primary = _primary_image(images)
    return ProductCard(
        id=product.id,
        slug=product.slug,
        name=product.name,
        brand=product.brand,
        category_slug=product.category.slug,
        category_name=product.category.name,
        subtype=product.subtype,
        short_description=product.short_description,
        price_inr=_money(product.price_inr) or "0.00",
        box_price_inr=_money(product.box_price_inr),
        units_per_box=product.units_per_box,
        units_per_pack=product.units_per_pack,
        stock_qty=product.stock_qty,
        low_stock=0 < product.stock_qty <= product.low_stock_threshold,
        in_stock=product.stock_qty > 0,
        origin_country=product.origin_country,
        origin_label=product.origin_label,
        smoking_time_min_minutes=product.smoking_time_min_minutes,
        smoking_time_max_minutes=product.smoking_time_max_minutes,
        intensity=product.intensity,
        strength=product.strength,
        shape=product.shape,
        size_label=_size_label(product),
        is_founder_pick=product.is_founder_pick,
        founder_rank=product.founder_rank,
        is_new_arrival=product.is_new_arrival,
        primary_image=_image_public(primary) if primary is not None else None,
        ratings=[_rating_public(row) for row in visible],
        extra_ratings_count=max(0, len(ratings) - len(visible)),
    )


def _detail(product: Product) -> ProductDetail:
    payload = _card(product).model_dump()
    payload["description"] = product.description
    payload["sku"] = product.sku
    payload["images"] = [_image_public(row) for row in _ordered_images(product)]
    payload["ratings"] = [_rating_public(row) for row in _ordered_ratings(product)]
    payload["extra_ratings_count"] = 0
    return ProductDetail(**payload)


def _ordered_ratings(product: Product) -> list[ProductRating]:
    return sorted(product.ratings, key=lambda row: (row.sort_order, row.created_at, str(row.id)))


def _ordered_images(product: Product) -> list[ProductImage]:
    return sorted(product.images, key=lambda row: (row.sort_order, str(row.id)))


def _primary_image(images: list[ProductImage]) -> ProductImage | None:
    for image in images:
        if image.is_primary:
            return image
    return images[0] if images else None


def _image_public(image: ProductImage) -> ProductImagePublic:
    return ProductImagePublic(id=image.id, public_path=image.public_path, alt_text=image.alt_text)


def _rating_public(row: ProductRating) -> RatingPublic:
    return RatingPublic(source_name=row.source_name, score=_score(row.score))


def _size_label(product: Product) -> str | None:
    if product.size_label and product.size_label.strip():
        return product.size_label.strip()
    if product.length_inches is not None and product.ring_gauge is not None:
        rendered = f"{product.length_inches.quantize(Decimal('0.01')):.2f}".rstrip("0").rstrip(".")
        return f'{rendered}" × {product.ring_gauge}'
    return None


def _money(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"{value.quantize(Decimal('0.01')):.2f}"


def _score(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.1')):.1f}"


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _media_root() -> Path:
    return Path(__file__).resolve().parents[2] / "storage" / "products"
