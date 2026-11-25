import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.catalog import ProductShape, Strength


class CategoryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    description: str | None
    sort_order: int


class CategoryList(BaseModel):
    items: list[CategoryPublic]


class ProductImagePublic(BaseModel):
    id: uuid.UUID
    public_path: str
    alt_text: str


class RatingPublic(BaseModel):
    source_name: str
    score: str


class ProductCard(BaseModel):
    """Public card. `short_description` is included so accessory cards can show their one line."""

    id: uuid.UUID
    slug: str
    name: str
    brand: str
    category_slug: str
    category_name: str
    subtype: str | None
    short_description: str | None
    price_inr: str
    box_price_inr: str | None
    units_per_box: int | None
    units_per_pack: int | None
    stock_qty: int
    low_stock: bool
    in_stock: bool
    origin_country: str | None
    origin_label: str | None
    smoking_time_min_minutes: int | None
    smoking_time_max_minutes: int | None
    intensity: int | None
    strength: Strength | None
    shape: ProductShape | None
    size_label: str | None
    is_founder_pick: bool
    founder_rank: int | None
    is_new_arrival: bool
    primary_image: ProductImagePublic | None
    ratings: list[RatingPublic]
    extra_ratings_count: int


class ProductDetail(ProductCard):
    description: str | None
    sku: str
    images: list[ProductImagePublic]


class ProductCardPage(BaseModel):
    items: list[ProductCard]
    total: int
    page: int
    page_size: int


class ProductCardList(BaseModel):
    items: list[ProductCard]


class BrandList(BaseModel):
    items: list[str]


class PageQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=12, ge=1, le=48)
