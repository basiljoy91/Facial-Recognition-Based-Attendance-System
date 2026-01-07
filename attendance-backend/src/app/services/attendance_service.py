from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.errors import DuplicateAttendance, WindowViolation
from app.db.models import AttendanceTypeEnum
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.audit_repository import AuditRepository


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.attendance_repo = AttendanceRepository(db)
        self.audit_repo = AuditRepository(db)

    def _within_window(self, now: datetime) -> bool:
        start = datetime.combine(now.date(), time.fromisoformat(self.settings.attendance_window_start)).replace(tzinfo=timezone.utc)
        end = datetime.combine(now.date(), time.fromisoformat(self.settings.attendance_window_end)).replace(tzinfo=timezone.utc)
        grace = timedelta(minutes=self.settings.attendance_grace_minutes)
        return start - grace <= now <= end + grace

    def record(
        self,
        user_id: int,
        match_score: float,
        liveness_score: int | None,
        manual_override: bool = False,
        metadata: dict | None = None,
    ):
        now = datetime.now(timezone.utc)
        if not self._within_window(now) and not manual_override:
            raise WindowViolation("Outside allowed attendance window")

        last_log = self.attendance_repo.get_last_log(user_id)
        if last_log:
            cooldown = timedelta(minutes=self.settings.duplicate_cooldown_minutes)
            if now - last_log.timestamp < cooldown and not manual_override:
                raise DuplicateAttendance("Duplicate within cooldown window")

        attendance_date = date.today()
        log_type = AttendanceTypeEnum.CLOCK_IN
        existing_clock_in = self.attendance_repo.get_today_log(user_id, attendance_date, AttendanceTypeEnum.CLOCK_IN)
        if existing_clock_in and not manual_override:
            log_type = AttendanceTypeEnum.CLOCK_OUT

        confidence_int = int(match_score * 100)
        log = self.attendance_repo.create_log(
            user_id=user_id,
            attendance_date=attendance_date,
            log_type=log_type,
            confidence=confidence_int,
            liveness_score=liveness_score,
            manual_override=manual_override,
            metadata=metadata,
        )

        if self.settings.audit_log_enabled:
            self.audit_repo.log(
                action="attendance_mark",
                entity="attendance_logs",
                entity_id=str(log.id),
                details={"user_id": user_id, "type": log_type.value, "confidence": confidence_int},
            )

        return log

