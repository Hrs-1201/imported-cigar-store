import uuid
from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalog import Category, Product, ProductImage


def _contains(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class CatalogRepository:
    def list_categories(self, db: Session) -> Sequence[Category]:
        return db.scalars(select(Category).order_by(Category.sort_order, Category.slug)).all()

    def get_category_by_slug(self, db: Session, slug: str) -> Category | None:
        return db.scalar(select(Category).where(Category.slug == slug))

    def get_public_by_slug(self, db: Session, slug: str) -> Product | None:
        stmt = self._cards(
            select(Product).where(
                Product.slug == slug,
                Product.deleted_at.is_(None),
                Product.is_published.is_(True),
            )
        )
        return db.scalars(stmt).unique().one_or_none()

    def get_image_by_key(self, db: Session, storage_key: str) -> ProductImage | None:
        stmt = (
            select(ProductImage)
            .where(ProductImage.storage_key == storage_key)
            .options(joinedload(ProductImage.product))
        )
        return db.scalars(stmt).unique().first()

    def page_public(
        self,
        db: Session,
        *,
        category_id: uuid.UUID | None,
        q: str | None,
        origin: str | None,
        new_only: bool,
        page: int,
        page_size: int,
    ) -> tuple[Sequence[Product], int]:
        filters = self._filters(category_id=category_id, q=q, origin=origin, new_only=new_only)
        total = int(db.scalar(select(func.count(Product.id)).where(*filters)) or 0)
        order = (Product.created_at.desc(), Product.name.asc()) if new_only else (Product.name.asc(), Product.id.asc())
        stmt = (
            self._cards(select(Product).where(*filters))
            .order_by(*order)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return db.scalars(stmt).unique().all(), total

    def featured(self, db: Session, *, limit: int = 12) -> Sequence[Product]:
        cigar_ids = select(Category.id).where(Category.slug == "cigars")
        stmt = (
            self._cards(
                select(Product).where(
                    Product.deleted_at.is_(None),
                    Product.is_published.is_(True),
                    Product.is_founder_pick.is_(True),
                    Product.category_id.in_(cigar_ids),
                )
            )
            .order_by(Product.founder_rank.asc(), Product.name.asc())
            .limit(limit)
        )
        return db.scalars(stmt).unique().all()

    def new_arrivals(self, db: Session, *, limit: int = 12) -> Sequence[Product]:
        stmt = (
            self._cards(
                select(Product).where(
                    Product.deleted_at.is_(None),
                    Product.is_published.is_(True),
                    Product.is_new_arrival.is_(True),
                )
            )
            .order_by(Product.created_at.desc(), Product.name.asc())
            .limit(limit)
        )
        return db.scalars(stmt).unique().all()

    def brands(self, db: Session) -> list[str]:
        rows = db.scalars(
            select(Product.brand)
            .where(Product.deleted_at.is_(None), Product.is_published.is_(True))
            .distinct()
            .order_by(Product.brand.asc())
        ).all()
        return list(rows)

    def _filters(
        self,
        *,
        category_id: uuid.UUID | None,
        q: str | None,
        origin: str | None,
        new_only: bool,
    ) -> list:
        filters: list = [Product.deleted_at.is_(None), Product.is_published.is_(True)]
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if q:
            pattern = _contains(q)
            filters.append(
                or_(
                    Product.name.ilike(pattern, escape="\\"),
                    Product.brand.ilike(pattern, escape="\\"),
                )
            )
        if origin:
            filters.append(func.lower(Product.origin_country) == origin.strip().lower())
        if new_only:
            filters.append(Product.is_new_arrival.is_(True))
        return filters

    def _cards(self, stmt):
        return stmt.options(
            joinedload(Product.category),
            selectinload(Product.images),
            selectinload(Product.ratings),
        )
