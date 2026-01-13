from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.models import AttendanceLog, AttendanceTypeEnum


class AtendanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_last_log(self, user_id: int) -> Optional[AttendanceLog]:
        stmt = (
            select(AttendanceLog)
            .where(AttendanceLog.user_id == user_id)
            .order_by(AttendanceLog.timestamp.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def get_today_log(self, user_id: int, attendance_date: date, log_type: AttendanceTypeEnum) -> Optional[AttendanceLog]:
        stmt = (
            select(AttendanceLog)
            .where(
                and_(
                    AttendanceLog.user_id == user_id,
                    AttendanceLog.date == attendance_date,
                    AttendanceLog.type == log_type.value,
                )
            )
            .limit(1)
        )
        return self.db.scalar(stmt)

    def create_log(
        self,
        user_id: int,
        attendance_date: date,
        log_type: AttendanceTypeEnum,
        confidence: int,
        liveness_score: Optional[int],
        manual_override: bool = False,
        metadata: Optional[dict] = None,
    ) -> AttendanceLog:
        log = AttendanceLog(
            user_id=user_id,
            date=attendance_date,
            type=log_type.value,
            confidence=confidence,
            liveness_score=liveness_score,
            manual_override=manual_override,
            extra_data=metadata,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def get_recent_logs(self, limit: int = 50) -> list[AttendanceLog]:
        stmt = select(AttendanceLog).order_by(AttendanceLog.timestamp.desc()).limit(limit)
        return list(self.db.scalars(stmt))

