from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, action: str, entity: str, entity_id: Optional[str], details: Optional[dict]) -> AuditLog:
        record = AuditLog(action=action, entity=entity, entity_id=entity_id, details=details)
        self.db.add(record)
        self.db.flush()
        return record

