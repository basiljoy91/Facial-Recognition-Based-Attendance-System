from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RoleEnum, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, full_name: str, roll_no: str, role: RoleEnum, external_id: str, password_hash: str) -> User:
        user = User(
            full_name=full_name,
            roll_no=roll_no,
            role=role.value,
            external_id=external_id,
            password_hash=password_hash,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def get_by_external_id(self, external_id: str) -> User | None:
        return self.db.scalar(select(User).where(User.external_id == external_id))

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_admin(self) -> User | None:
        return self.db.scalar(select(User).where(User.role == RoleEnum.ADMIN.value))

