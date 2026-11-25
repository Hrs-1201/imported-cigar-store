from sqlalchemy.orm import Session

from app.models.contact import ContactMessage, ContactStatus
from app.repositories.contact_repo import ContactRepository
from app.schemas.contact import ContactCreated, ContactRequest

_repo = ContactRepository()


def create_message(db: Session, body: ContactRequest) -> ContactCreated:
    row = _repo.add(
        db,
        ContactMessage(
            name=body.name,
            email=str(body.email),
            phone=body.phone,
            subject=body.subject,
            message=body.message,
            status=ContactStatus.new,
        ),
    )
    db.commit()
    db.refresh(row)
    return ContactCreated(id=row.id, status=row.status)
