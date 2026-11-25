import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import RefreshToken, User


class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    def get_by_id(self, db: Session, user_id: uuid.UUID) -> User | None:
        return db.get(User, user_id)

    def add_user(self, db: Session, user: User) -> User:
        db.add(user)
        db.flush()
        return user

    def get_refresh_by_hash(self, db: Session, token_hash: str) -> RefreshToken | None:
        return db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    def add_refresh(self, db: Session, token: RefreshToken) -> RefreshToken:
        db.add(token)
        db.flush()
        return token
