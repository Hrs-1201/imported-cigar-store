import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Strength(str, enum.Enum):
    mild = "mild"
    mild_to_medium = "mild_to_medium"
    medium = "medium"
    medium_to_full = "medium_to_full"
    full = "full"


class ProductShape(str, enum.Enum):
    parejo = "parejo"
    toro = "toro"
    robusto = "robusto"
    churchill = "churchill"
    figurado = "figurado"
    lancero = "lancero"
    corona = "corona"
    gordo = "gordo"
    other = "other"


def _enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        native_enum=True,
        values_callable=lambda members: [member.value for member in members],
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
    )

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_inr > 0", name="ck_products_price_inr"),
        CheckConstraint("stock_qty >= 0", name="ck_products_stock_qty"),
        CheckConstraint("intensity IS NULL OR intensity BETWEEN 1 AND 5", name="ck_products_intensity"),
        CheckConstraint(
            "(is_founder_pick = true AND founder_rank IS NOT NULL AND founder_rank >= 1) "
            "OR (is_founder_pick = false AND founder_rank IS NULL)",
            name="ck_products_founder_rank",
        ),
        Index(
            "ix_products_public_category",
            "category_id",
            postgresql_where=text("deleted_at IS NULL AND is_published"),
        ),
        Index("ix_products_founder", "is_founder_pick", "founder_rank"),
        Index("ix_products_brand", "brand"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("categories.id", name="fk_products_category_id"),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(120), nullable=False)
    subtype: Mapped[str | None] = mapped_column(String(64), nullable=True)
    short_description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    box_price_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    units_per_box: Mapped[int | None] = mapped_column(Integer, nullable=True)
    units_per_pack: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    low_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=2, server_default="2")
    origin_country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    origin_region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    origin_label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    smoking_time_min_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    smoking_time_max_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    intensity: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    strength: Mapped[Strength | None] = mapped_column(_enum(Strength, "strength"), nullable=True)
    shape: Mapped[ProductShape | None] = mapped_column(_enum(ProductShape, "product_shape"), nullable=True)
    length_inches: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    ring_gauge: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    size_label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_founder_pick: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    founder_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_new_arrival: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
    )

    category: Mapped[Category] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    ratings: Mapped[list["ProductRating"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ProductImage(Base):
    __tablename__ = "product_images"
    __table_args__ = (
        Index(
            "uq_product_images_one_primary",
            "product_id",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", name="fk_product_images_product_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    public_path: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, server_default=func.now()
    )

    product: Mapped[Product] = relationship(back_populates="images")


class ProductRating(Base):
    __tablename__ = "product_ratings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", name="fk_product_ratings_product_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_name: Mapped[str] = mapped_column(String(80), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, server_default=func.now()
    )

    product: Mapped[Product] = relationship(back_populates="ratings")
