import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.catalog_service import resolve_public_media

router = APIRouter(tags=["media"])

_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,200}$")


@router.get("/media/products/{storage_filename}")
def product_media(storage_filename: str, db: Annotated[Session, Depends(get_db)]) -> FileResponse:
    if not _FILENAME.fullmatch(storage_filename):
        raise HTTPException(status_code=404, detail="Image not found")
    path = resolve_public_media(db, storage_filename)
    if path is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)
