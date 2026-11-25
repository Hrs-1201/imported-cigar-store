from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.catalog import BrandList, CategoryList, ProductCardList, ProductCardPage, ProductDetail
from app.services import catalog_service
from app.services.catalog_service import CatalogNotFound

router = APIRouter(tags=["catalog"])


def _not_found(exc: CatalogNotFound) -> HTTPException:
    return HTTPException(status_code=404, detail=exc.detail)


@router.get("/categories", response_model=CategoryList)
def list_categories(db: Annotated[Session, Depends(get_db)]) -> CategoryList:
    return catalog_service.list_categories(db)


@router.get("/categories/{slug}/products", response_model=ProductCardPage)
def category_products(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=48)] = 12,
    origin: Annotated[str | None, Query(max_length=80)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
) -> ProductCardPage:
    try:
        return catalog_service.category_products(
            db, slug, q=q, origin=origin, page=page, page_size=page_size
        )
    except CatalogNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/products/featured", response_model=ProductCardList)
def featured_products(db: Annotated[Session, Depends(get_db)]) -> ProductCardList:
    return catalog_service.featured_products(db)


@router.get("/products/new-arrivals", response_model=ProductCardList)
def new_arrivals(db: Annotated[Session, Depends(get_db)]) -> ProductCardList:
    return catalog_service.new_arrival_products(db)


@router.get("/products", response_model=ProductCardPage)
def search_products(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str | None, Query(max_length=200)] = None,
    origin: Annotated[str | None, Query(max_length=80)] = None,
    new: Annotated[int | None, Query(ge=0, le=1)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=48)] = 12,
) -> ProductCardPage:
    return catalog_service.search_products(
        db,
        q=q,
        origin=origin,
        new_only=new == 1,
        page=page,
        page_size=page_size,
    )


@router.get("/products/{slug}", response_model=ProductDetail)
def product_detail(slug: str, db: Annotated[Session, Depends(get_db)]) -> ProductDetail:
    try:
        return catalog_service.get_product(db, slug)
    except CatalogNotFound as exc:
        raise _not_found(exc) from exc


@router.get("/brands", response_model=BrandList)
def list_brands(db: Annotated[Session, Depends(get_db)]) -> BrandList:
    return catalog_service.list_brands(db)
