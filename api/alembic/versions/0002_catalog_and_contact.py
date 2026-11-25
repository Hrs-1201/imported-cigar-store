"""catalog tables, contact messages, and the four departments

Revision ID: 0002_catalog
Revises: 0001_users
Create Date: 2026-11-25

"""

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_catalog"
down_revision = "0001_users"
branch_labels = None
depends_on = None

_CATEGORIES = (
    ("a0000000-0000-4000-8000-000000000001", "cigars", "Cigars", 1),
    ("a0000000-0000-4000-8000-000000000002", "cigarettes", "Cigarettes", 2),
    ("a0000000-0000-4000-8000-000000000003", "lighters", "Lighters", 3),
    ("a0000000-0000-4000-8000-000000000004", "accessories", "Accessories", 4),
)


def upgrade() -> None:
    strength = postgresql.ENUM(
        "mild",
        "mild_to_medium",
        "medium",
        "medium_to_full",
        "full",
        name="strength",
        create_type=False,
    )
    product_shape = postgresql.ENUM(
        "parejo",
        "toro",
        "robusto",
        "churchill",
        "figurado",
        "lancero",
        "corona",
        "gordo",
        "other",
        name="product_shape",
        create_type=False,
    )
    contact_status = postgresql.ENUM("new", "read", "archived", name="contact_status", create_type=False)
    bind = op.get_bind()
    strength.create(bind, checkfirst=True)
    product_shape.create(bind, checkfirst=True)
    contact_status.create(bind, checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=False),
        sa.Column("subtype", sa.String(length=64), nullable=True),
        sa.Column("short_description", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_inr", sa.Numeric(12, 2), nullable=False),
        sa.Column("box_price_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("units_per_box", sa.Integer(), nullable=True),
        sa.Column("units_per_pack", sa.Integer(), nullable=True),
        sa.Column("stock_qty", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("low_stock_threshold", sa.Integer(), nullable=False, server_default=sa.text("2")),
        sa.Column("origin_country", sa.String(length=80), nullable=True),
        sa.Column("origin_region", sa.String(length=120), nullable=True),
        sa.Column("origin_label", sa.String(length=160), nullable=True),
        sa.Column("smoking_time_min_minutes", sa.Integer(), nullable=True),
        sa.Column("smoking_time_max_minutes", sa.Integer(), nullable=True),
        sa.Column("intensity", sa.SmallInteger(), nullable=True),
        sa.Column("strength", strength, nullable=True),
        sa.Column("shape", product_shape, nullable=True),
        sa.Column("length_inches", sa.Numeric(4, 2), nullable=True),
        sa.Column("ring_gauge", sa.SmallInteger(), nullable=True),
        sa.Column("size_label", sa.String(length=80), nullable=True),
        sa.Column("is_founder_pick", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("founder_rank", sa.Integer(), nullable=True),
        sa.Column("is_new_arrival", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("price_inr > 0", name="ck_products_price_inr"),
        sa.CheckConstraint("stock_qty >= 0", name="ck_products_stock_qty"),
        sa.CheckConstraint("intensity IS NULL OR intensity BETWEEN 1 AND 5", name="ck_products_intensity"),
        sa.CheckConstraint(
            "(is_founder_pick = true AND founder_rank IS NOT NULL AND founder_rank >= 1) "
            "OR (is_founder_pick = false AND founder_rank IS NULL)",
            name="ck_products_founder_rank",
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name="fk_products_category_id"),
        sa.UniqueConstraint("sku", name="uq_products_sku"),
        sa.UniqueConstraint("slug", name="uq_products_slug"),
    )
    op.create_index(
        "ix_products_public_category",
        "products",
        ["category_id"],
        postgresql_where=sa.text("deleted_at IS NULL AND is_published"),
    )
    op.create_index("ix_products_founder", "products", ["is_founder_pick", "founder_rank"])
    op.create_index("ix_products_brand", "products", ["brand"])
    op.execute("CREATE INDEX ix_products_new_arrival ON products (is_new_arrival, created_at DESC)")

    op.create_table(
        "product_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("public_path", sa.Text(), nullable=False),
        sa.Column("alt_text", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_product_images_product_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_product_images_product_id", "product_images", ["product_id"])
    op.create_index(
        "uq_product_images_one_primary",
        "product_images",
        ["product_id"],
        unique=True,
        postgresql_where=sa.text("is_primary"),
    )

    op.create_table(
        "product_ratings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_name", sa.String(length=80), nullable=False),
        sa.Column("score", sa.Numeric(4, 1), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_product_ratings_product_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_product_ratings_product_id", "product_ratings", ["product_id"])

    op.create_table(
        "contact_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            contact_status,
            nullable=False,
            server_default=sa.text("'new'::contact_status"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    now = datetime.now(timezone.utc)
    categories = sa.table(
        "categories",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("sort_order", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        categories,
        [
            {
                "id": uuid.UUID(row_id),
                "slug": slug,
                "name": name,
                "description": None,
                "sort_order": sort_order,
                "created_at": now,
                "updated_at": now,
            }
            for row_id, slug, name, sort_order in _CATEGORIES
        ],
    )


def downgrade() -> None:
    op.drop_table("contact_messages")
    op.drop_index("ix_product_ratings_product_id", table_name="product_ratings")
    op.drop_table("product_ratings")
    op.drop_index("uq_product_images_one_primary", table_name="product_images")
    op.drop_index("ix_product_images_product_id", table_name="product_images")
    op.drop_table("product_images")
    op.execute("DROP INDEX IF EXISTS ix_products_new_arrival")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_index("ix_products_founder", table_name="products")
    op.drop_index("ix_products_public_category", table_name="products")
    op.drop_table("products")
    op.drop_table("categories")
    bind = op.get_bind()
    postgresql.ENUM(name="contact_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="product_shape").drop(bind, checkfirst=True)
    postgresql.ENUM(name="strength").drop(bind, checkfirst=True)
