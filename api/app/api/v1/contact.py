from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.contact import ContactCreated, ContactRequest
from app.services.contact_service import create_message

router = APIRouter(tags=["contact"])


@router.post("/contact", response_model=ContactCreated, status_code=201)
def post_contact(body: ContactRequest, db: Annotated[Session, Depends(get_db)]) -> ContactCreated:
    return create_message(db, body)
