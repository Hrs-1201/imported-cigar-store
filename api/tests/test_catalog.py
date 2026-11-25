from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Category, Product, ProductImage, ProductRating, ProductShape, Strength
from app.models.contact import ContactMessage, ContactStatus

CARD_KEYS = {
    "id",
    "slug",
    "name",
    "brand",
    "category_slug",
    "category_name",
    "subtype",
    "short_description",
    "price_inr",
    "box_price_inr",
    "units_per_box",
    "units_per_pack",
    "stock_qty",
    "low_stock",
    "in_stock",
    "origin_country",
    "origin_label",
    "smoking_time_min_minutes",
    "smoking_time_max_minutes",
    "intensity",
    "strength",
    "shape",
    "size_label",
    "is_founder_pick",
    "founder_rank",
    "is_new_arrival",
    "primary_image",
    "ratings",
    "extra_ratings_count",
}


def _product(db: Session, **overrides) -> Product:
    token = uuid4().hex[:8]
    category_slug = overrides.pop("category_slug", "cigars")
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    assert category is not None
    values = {
        "category_id": category.id,
        "sku": f"SKU-{token}",
        "slug": f"product-{token}",
        "name": f"Product {token}",
        "brand": "Sample Brand",
        "price_inr": Decimal("100.00"),
        "stock_qty": 5,
        "is_published": True,
    }
    values.update(overrides)
    product = Product(**values)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def test_categories_are_the_four_departments(client):
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    body = response.json()
    assert [item["slug"] for item in body["items"]] == ["cigars", "cigarettes", "lighters", "accessories"]
    assert [item["name"] for item in body["items"]] == ["Cigars", "Cigarettes", "Lighters", "Accessories"]
    assert [item["sort_order"] for item in body["items"]] == [1, 2, 3, 4]


def test_published_products_are_listed_and_hidden_ones_are_not(client, db_session):
    visible = _product(
        db_session,
        name="Visible Cedar",
        brand="Sample Habano",
        slug="visible-cedar",
        sku="SKU-VISIBLE",
        origin_country="Cuba",
        stock_qty=1,
        low_stock_threshold=2,
        length_inches=Decimal("6.00"),
        ring_gauge=52,
        strength=Strength.medium_to_full,
        shape=ProductShape.figurado,
        is_founder_pick=True,
        founder_rank=1,
    )
    hidden = _product(
        db_session,
        name="Hidden Drawer Stick",
        brand="Secret Brand Only",
        slug="hidden-drawer-stick",
        sku="SKU-HIDDEN",
        is_published=False,
        origin_country="Cuba",
    )
    removed = _product(
        db_session,
        name="Removed Stick",
        slug="removed-stick",
        sku="SKU-REMOVED",
        is_published=True,
        deleted_at=datetime.now(timezone.utc),
    )
    db_session.add_all(
        [
            ProductRating(
                product_id=visible.id,
                source_name="Third",
                score=Decimal("91.0"),
                sort_order=2,
            ),
            ProductRating(
                product_id=visible.id,
                source_name="First",
                score=Decimal("96.0"),
                sort_order=0,
            ),
            ProductRating(
                product_id=visible.id,
                source_name="Second",
                score=Decimal("94.5"),
                sort_order=1,
            ),
            ProductImage(
                product_id=visible.id,
                storage_key=f"visible-{visible.id}.webp",
                public_path=f"/api/v1/media/products/visible-{visible.id}.webp",
                alt_text="Visible Cedar",
                sort_order=0,
                is_primary=True,
            ),
        ]
    )
    db_session.commit()

    listed = client.get("/api/v1/categories/cigars/products")
    assert listed.status_code == 200
    page = listed.json()
    assert page["total"] == 1
    assert page["page"] == 1
    assert page["page_size"] == 12
    assert [item["slug"] for item in page["items"]] == ["visible-cedar"]
    card = page["items"][0]
    assert set(card) == CARD_KEYS
    assert "sku" not in card
    assert "deleted_at" not in card
    assert "is_published" not in card
    assert card["price_inr"] == "100.00"
    assert card["low_stock"] is True
    assert card["in_stock"] is True
    assert card["size_label"] == '6" × 52'
    assert card["strength"] == "medium_to_full"
    assert card["category_slug"] == "cigars"
    assert card["primary_image"]["alt_text"] == "Visible Cedar"
    assert card["primary_image"]["public_path"].endswith(".webp")
    assert [row["source_name"] for row in card["ratings"]] == ["First", "Second"]
    assert card["ratings"][0]["score"] == "96.0"
    assert card["extra_ratings_count"] == 1

    detail = client.get("/api/v1/products/visible-cedar")
    assert detail.status_code == 200
    body = detail.json()
    assert body["sku"] == "SKU-VISIBLE"
    assert [row["source_name"] for row in body["ratings"]] == ["First", "Second", "Third"]
    assert body["extra_ratings_count"] == 0
    assert len(body["images"]) == 1

    assert client.get(f"/api/v1/products/{hidden.slug}").status_code == 404
    assert client.get(f"/api/v1/products/{removed.slug}").status_code == 404
    assert client.get("/api/v1/products/does-not-exist").status_code == 404

    search = client.get("/api/v1/products", params={"q": "Secret Brand"})
    assert search.status_code == 200
    assert search.json()["items"] == []

    featured = client.get("/api/v1/products/featured")
    assert [item["slug"] for item in featured.json()["items"]] == ["visible-cedar"]

    brands = client.get("/api/v1/brands")
    assert brands.json()["items"] == ["Sample Habano"]

    media = client.get(card["primary_image"]["public_path"])
    assert media.status_code == 404


def test_unknown_category_slug_is_404(client):
    response = client.get("/api/v1/categories/samplers/products")
    assert response.status_code == 404


def test_empty_category_is_an_empty_page(client):
    response = client.get("/api/v1/categories/accessories/products")
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_search_matches_name_or_brand_and_stays_empty_without_a_query(client, db_session):
    _product(db_session, name="North Pack", brand="Sample Drawer", slug="north-pack", sku="SKU-NORTH", category_slug="cigarettes")
    _product(db_session, name="Other Stick", brand="Sample Habano", slug="other-stick", sku="SKU-OTHER")

    idle = client.get("/api/v1/products")
    assert idle.status_code == 200
    assert idle.json()["items"] == []
    assert idle.json()["total"] == 0

    by_origin_only = client.get("/api/v1/products", params={"origin": "Cuba"})
    assert by_origin_only.json()["items"] == []

    by_name = client.get("/api/v1/products", params={"q": "north"})
    assert [item["slug"] for item in by_name.json()["items"]] == ["north-pack"]

    by_brand = client.get("/api/v1/products", params={"q": "habano"})
    assert [item["slug"] for item in by_brand.json()["items"]] == ["other-stick"]

    escaped = client.get("/api/v1/products", params={"q": "%"})
    assert escaped.json()["items"] == []


def test_new_flag_returns_newest_arrivals_and_can_combine_with_query(client, db_session):
    older = datetime(2026, 11, 1, tzinfo=timezone.utc)
    newer = older + timedelta(days=3)
    _product(
        db_session,
        name="Older Arrival",
        slug="older-arrival",
        sku="SKU-OLDER",
        is_new_arrival=True,
        created_at=older,
        updated_at=older,
    )
    _product(
        db_session,
        name="Newer Arrival",
        slug="newer-arrival",
        sku="SKU-NEWER",
        brand="Fresh Shelf",
        is_new_arrival=True,
        created_at=newer,
        updated_at=newer,
    )
    _product(db_session, name="Not New", slug="not-new", sku="SKU-STEADY", is_new_arrival=False)

    listed = client.get("/api/v1/products", params={"new": 1})
    assert [item["slug"] for item in listed.json()["items"]] == ["newer-arrival", "older-arrival"]

    narrowed = client.get("/api/v1/products", params={"new": 1, "q": "fresh"})
    assert [item["slug"] for item in narrowed.json()["items"]] == ["newer-arrival"]

    capped = client.get("/api/v1/products/new-arrivals")
    assert [item["slug"] for item in capped.json()["items"]] == ["newer-arrival", "older-arrival"]


def test_origin_filter_is_case_insensitive_on_every_category(client, db_session):
    _product(
        db_session,
        name="Cuban Demo",
        slug="cuban-demo",
        sku="SKU-CUBA",
        origin_country="Cuba",
    )
    _product(
        db_session,
        name="Other Island",
        slug="other-island",
        sku="SKU-OTHER-ISLAND",
        origin_country="Nicaragua",
    )
    _product(
        db_session,
        name="Danish Pack",
        slug="danish-pack",
        sku="SKU-DK",
        category_slug="cigarettes",
        origin_country="Denmark",
        units_per_pack=20,
        strength=Strength.medium,
    )
    _product(
        db_session,
        name="Belgian Pack",
        slug="belgian-pack",
        sku="SKU-BE",
        category_slug="cigarettes",
        origin_country="Belgium",
    )

    cigars = client.get("/api/v1/categories/cigars/products", params={"origin": "cuba"})
    assert [item["slug"] for item in cigars.json()["items"]] == ["cuban-demo"]

    cigarettes = client.get("/api/v1/categories/cigarettes/products", params={"origin": "Denmark"})
    assert [item["slug"] for item in cigarettes.json()["items"]] == ["danish-pack"]

    with_query = client.get("/api/v1/products", params={"q": "pack", "origin": "denmark"})
    assert [item["slug"] for item in with_query.json()["items"]] == ["danish-pack"]


def test_featured_is_published_cigars_only_ordered_by_rank(client, db_session):
    _product(
        db_session,
        name="Second Pick",
        slug="second-pick",
        sku="SKU-RANK-2",
        is_founder_pick=True,
        founder_rank=2,
    )
    _product(
        db_session,
        name="First Pick",
        slug="first-pick",
        sku="SKU-RANK-1",
        is_founder_pick=True,
        founder_rank=1,
    )
    _product(
        db_session,
        name="Hidden Pick",
        slug="hidden-pick",
        sku="SKU-RANK-HIDDEN",
        is_founder_pick=True,
        founder_rank=3,
        is_published=False,
    )
    _product(
        db_session,
        name="Plain Cigar",
        slug="plain-cigar",
        sku="SKU-PLAIN",
        is_founder_pick=False,
    )
    _product(
        db_session,
        name="Lighter Pick",
        slug="lighter-pick",
        sku="SKU-LIGHTER-PICK",
        category_slug="lighters",
        is_founder_pick=True,
        founder_rank=1,
    )

    response = client.get("/api/v1/products/featured")
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["items"]] == ["first-pick", "second-pick"]


def test_out_of_stock_stays_public_without_the_low_stock_flag(client, db_session):
    _product(db_session, name="Empty Box", slug="empty-box", sku="SKU-EMPTY", stock_qty=0, low_stock_threshold=2)
    response = client.get("/api/v1/categories/cigars/products")
    card = response.json()["items"][0]
    assert card["in_stock"] is False
    assert card["low_stock"] is False
    assert card["stock_qty"] == 0


def test_typed_size_label_wins(client, db_session):
    _product(
        db_session,
        name="King",
        slug="king-size",
        sku="SKU-KING",
        size_label="King size",
        length_inches=Decimal("6.00"),
        ring_gauge=52,
    )
    card = client.get("/api/v1/products/king-size").json()
    assert card["size_label"] == "King size"


def test_page_size_is_capped(client):
    response = client.get("/api/v1/products", params={"q": "a", "page_size": 49})
    assert response.status_code == 422


def test_contact_saves_a_message(client, db_session):
    response = client.post(
        "/api/v1/contact",
        json={
            "name": "  Asha Rao  ",
            "email": "Asha@Example.com",
            "phone": "",
            "subject": "Stock question",
            "message": "Do you ship to Guwahati?",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert set(body) == {"id", "status"}
    assert body["status"] == "new"
    db_session.expire_all()
    row = db_session.get(ContactMessage, body["id"])
    assert row is not None
    assert row.name == "Asha Rao"
    assert row.email == "asha@example.com"
    assert row.phone is None
    assert row.subject == "Stock question"
    assert row.status == ContactStatus.new

    invalid = client.post(
        "/api/v1/contact",
        json={"name": "Asha", "email": "not-an-email", "subject": "Hi", "message": "Hello"},
    )
    assert invalid.status_code == 422


def test_missing_media_file_is_404(client):
    response = client.get("/api/v1/media/products/missing.webp")
    assert response.status_code == 404
    assert client.get("/api/v1/media/products/../secrets").status_code == 404
