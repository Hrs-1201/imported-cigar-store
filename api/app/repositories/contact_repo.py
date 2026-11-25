from sqlalchemy.orm import Session

from app.models.contact import ContactMessage


class ContactRepository:
    def add(self, db: Session, row: ContactMessage) -> ContactMessage:
        db.add(row)
        db.flush()
        return row
